import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import prisma from '../lib/prisma';
import { authMiddleware, AuthRequest } from '../middleware/auth.middleware';

const router = Router();

function signToken(user: { id: string; email: string; plan: string }): string {
  const secret = (process.env.JWT_SECRET || 'dev-secret') as jwt.Secret;
  const expires = process.env.JWT_EXPIRATION || '24h';
  const options: jwt.SignOptions = { expiresIn: expires as unknown as jwt.SignOptions['expiresIn'] };
  return jwt.sign({ userId: user.id, email: user.email, plan: user.plan }, secret, options);
}

// POST /api/auth/register
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Email y password son requeridos' });
      return;
    }

    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      res.status(409).json({ error: 'Email ya registrado' });
      return;
    }

    const hashed = await bcrypt.hash(password, 12);
    const user = await prisma.user.create({
      data: { email, password: hashed, name, plan: 'FREE' },
    });

    const token = signToken(user);
    res.status(201).json({
      token,
      user: { id: user.id, email: user.email, name: user.name, plan: user.plan },
    });
  } catch (err) {
    res.status(500).json({ error: 'Error al registrar usuario' });
  }
});

// POST /api/auth/login
router.post('/login', async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Email y password son requeridos' });
      return;
    }

    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      res.status(401).json({ error: 'Credenciales invalidas' });
      return;
    }

    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      res.status(401).json({ error: 'Credenciales invalidas' });
      return;
    }

    const token = signToken(user);
    res.json({
      token,
      user: { id: user.id, email: user.email, name: user.name, plan: user.plan },
    });
  } catch (err) {
    res.status(500).json({ error: 'Error al iniciar sesion' });
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
      res.status(404).json({ error: 'Usuario no encontrado' });
      return;
    }

    res.json({ user });
  } catch (err) {
    res.status(500).json({ error: 'Error al obtener usuario' });
  }
});

// PATCH /api/auth/plan
router.patch('/plan', authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { plan } = req.body;
    const validPlans = ['FREE', 'BASICO', 'AVANZADO', 'PREMIUM'];

    if (!validPlans.includes(plan)) {
      res.status(400).json({ error: 'Plan invalido', validPlans });
      return;
    }

    const user = await prisma.user.update({
      where: { id: req.user!.userId },
      data: { plan },
      select: { id: true, email: true, name: true, plan: true },
    });

    // Issue new token with updated plan
    const token = signToken(user);
    res.json({ token, user });
  } catch (err) {
    res.status(500).json({ error: 'Error al actualizar plan' });
  }
});

export default router;
