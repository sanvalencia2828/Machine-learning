import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { Plan } from '@prisma/client';
import prisma from '../lib/prisma.js';
import { authMiddleware, AuthRequest } from '../middleware/auth.middleware.js';
import { ResponseCode } from '../types/errors.js';

const router = Router();

const ACCESS_SECRET = () => (process.env.JWT_SECRET || 'dev-secret') as jwt.Secret;
const REFRESH_EXPIRY_DAYS = 7;

function signAccessToken(user: { id: string; email: string; plan: string }): string {
  return jwt.sign(
    { userId: user.id, email: user.email, plan: user.plan, type: 'access' },
    ACCESS_SECRET(),
    { expiresIn: '15m' } as jwt.SignOptions
  );
}

async function createRefreshToken(userId: string): Promise<string> {
  const token = crypto.randomBytes(64).toString('hex');
  const expiresAt = new Date(Date.now() + REFRESH_EXPIRY_DAYS * 24 * 60 * 60 * 1000);

  await prisma.refreshToken.create({
    data: { token, userId, expiresAt },
  });

  return token;
}

async function issueTokenPair(user: { id: string; email: string; plan: string }) {
  const accessToken = signAccessToken(user);
  const refreshToken = await createRefreshToken(user.id);
  return { accessToken, refreshToken };
}

// POST /api/auth/register
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password) {
      res.status(400).json({
        code: ResponseCode.BAD_REQUEST,
        message: 'Email y password son requeridos',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      res.status(409).json({
        code: ResponseCode.CONFLICT,
        message: 'Email ya registrado',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    const hashed = await bcrypt.hash(password, 12);
    const user = await prisma.user.create({
      data: { email, password: hashed, name, plan: Plan.FREE },
    });

    const tokens = await issueTokenPair(user);
    res.status(201).json({
      ...tokens,
      user: { id: user.id, email: user.email, name: user.name, plan: user.plan },
    });
  } catch (err) {
    res.status(500).json({
      code: ResponseCode.INTERNAL_ERROR,
      message: 'Error al registrar usuario',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  }
});

// POST /api/auth/login
router.post('/login', async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({
        code: ResponseCode.BAD_REQUEST,
        message: 'Email y password son requeridos',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      res.status(401).json({
        code: ResponseCode.AUTHENTICATION_ERROR,
        message: 'Credenciales invalidas',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      res.status(401).json({
        code: ResponseCode.AUTHENTICATION_ERROR,
        message: 'Credenciales invalidas',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    // Limpiar refresh tokens viejos (max 5 activos por usuario)
    const existing = await prisma.refreshToken.findMany({
      where: { userId: user.id, revoked: false },
      orderBy: { createdAt: 'desc' },
    });
    if (existing.length >= 5) {
      const toRevoke = existing.slice(4).map((t: { id: string }) => t.id);
      await prisma.refreshToken.updateMany({
        where: { id: { in: toRevoke } },
        data: { revoked: true },
      });
    }

    const tokens = await issueTokenPair(user);
    res.json({
      ...tokens,
      user: { id: user.id, email: user.email, name: user.name, plan: user.plan },
    });
  } catch (err) {
    res.status(500).json({
      code: ResponseCode.INTERNAL_ERROR,
      message: 'Error al iniciar sesion',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  }
});

// POST /api/auth/refresh — rotate refresh token, issue new pair
router.post('/refresh', async (req: Request, res: Response) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      res.status(400).json({
        code: ResponseCode.BAD_REQUEST,
        message: 'Refresh token requerido',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    const stored = await prisma.refreshToken.findUnique({
      where: { token: refreshToken },
      include: { user: true },
    });

    if (!stored || stored.revoked || stored.expiresAt < new Date()) {
      // Si ya fue revocado, posible robo -> revocar TODOS del usuario
      if (stored?.revoked) {
        await prisma.refreshToken.updateMany({
          where: { userId: stored.userId },
          data: { revoked: true },
        });
      }
      res.status(401).json({
        code: ResponseCode.AUTHENTICATION_ERROR,
        message: 'Refresh token invalido o expirado',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    // Rotate: revocar viejo, emitir nuevo par
    await prisma.refreshToken.update({
      where: { id: stored.id },
      data: { revoked: true },
    });

    const user = stored.user;
    const tokens = await issueTokenPair(user);
    res.json({
      ...tokens,
      user: { id: user.id, email: user.email, name: user.name, plan: user.plan },
    });
  } catch (err) {
    res.status(500).json({
      code: ResponseCode.INTERNAL_ERROR,
      message: 'Error al refrescar token',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  }
});

// POST /api/auth/logout — revoke refresh token
router.post('/logout', async (req: Request, res: Response) => {
  try {
    const { refreshToken } = req.body;
    if (refreshToken) {
      await prisma.refreshToken.updateMany({
        where: { token: refreshToken },
        data: { revoked: true },
      });
    }
    res.json({
      message: 'Sesion cerrada',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  } catch {
    res.json({
      message: 'Sesion cerrada',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  }
});

// GET /api/auth/me
router.get('/me', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user!.userId },
      select: { id: true, email: true, name: true, plan: true, createdAt: true },
    });

    if (!user) {
      res.status(404).json({
        code: ResponseCode.NOT_FOUND,
        message: 'Usuario no encontrado',
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    res.json({ user });
  } catch (err) {
    res.status(500).json({
      code: ResponseCode.INTERNAL_ERROR,
      message: 'Error al obtener usuario',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  }
});

// PATCH /api/auth/plan
router.patch('/plan', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { plan } = req.body as { plan: Plan };

    if (!Object.values(Plan).includes(plan)) {
      res.status(400).json({
        code: ResponseCode.BAD_REQUEST,
        message: 'Plan invalido',
        validPlans: Object.values(Plan),
        meta: {
          timestamp: new Date().toISOString(),
          correlationId: 'unknown',
          path: req.path,
          method: req.method,
        }
      });
      return;
    }

    const user = await prisma.user.update({
      where: { id: req.user!.userId },
      data: { plan },
      select: { id: true, email: true, name: true, plan: true },
    });

    const accessToken = signAccessToken(user);
    res.json({ accessToken, user });
  } catch (err) {
    res.status(500).json({
      code: ResponseCode.INTERNAL_ERROR,
      message: 'Error al actualizar plan',
      meta: {
        timestamp: new Date().toISOString(),
        correlationId: 'unknown',
        path: req.path,
        method: req.method,
      }
    });
  }
});

export default router;
