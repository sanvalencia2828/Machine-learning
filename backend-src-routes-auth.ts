import { Router, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { prisma } from '../lib/prisma';

const router = Router();

// Zod schemas for validation
const LoginRequestSchema = z.object({
  oauthProvider: z.enum(['google', 'github', 'microsoft']),
  oauthId: z.string().min(1),
  email: z.string().email(),
  name: z.string().optional()
});

// OAuth Callback Handler
router.post('/oauth-callback', async (req: Request, res: Response) => {
  try {
    const { oauthProvider, oauthId, email, name } = LoginRequestSchema.parse(req.body);

    // Find or create user
    let user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user) {
      user = await prisma.user.create({
        data: {
          email,
          name: name || email.split('@')[0],
          oauthProvider,
          oauthId,
          emailVerified: true // OAuth providers verify email
        }
      });

      // Assign default "student" role to new users
      const studentRole = await prisma.role.findUnique({
        where: { name: 'student' }
      });

      if (studentRole) {
        await prisma.userRole.create({
          data: {
            userId: user.id,
            roleId: studentRole.id
          }
        });
      }
    } else if (user.oauthProvider !== oauthProvider || user.oauthId !== oauthId) {
      // Update OAuth info if changed
      user = await prisma.user.update({
        where: { id: user.id },
        data: { oauthProvider, oauthId }
      });
    }

    // Update last login
    await prisma.user.update({
      where: { id: user.id },
      data: { lastLogin: new Date() }
    });

    // Log audit event
    await prisma.auditLog.create({
      data: {
        userId: user.id,
        action: 'login',
        resourceType: 'auth',
        status: 'success',
        ipAddress: req.ip || undefined,
        userAgent: req.headers['user-agent']
      }
    });

    // Generate JWT
    const jwtSecret = process.env.JWT_SECRET;
    const refreshSecret = process.env.REFRESH_TOKEN_SECRET;
    if (!jwtSecret || !refreshSecret) {
      throw new Error('JWT_SECRET and REFRESH_TOKEN_SECRET must be set');
    }

    const token = jwt.sign(
      { userId: user.id },
      jwtSecret,
      { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
      { userId: user.id },
      refreshSecret,
      { expiresIn: '7d' }
    );

    res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      },
      tokens: {
        access: token,
        refresh: refreshToken
      }
    });
  } catch (error) {
    console.error('OAuth callback error:', error);
    
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.errors
      });
    }

    res.status(500).json({ error: 'Authentication failed' });
  }
});

// Refresh Token Endpoint
router.post('/refresh', async (req: Request, res: Response) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token required' });
    }

    const refreshSecret = process.env.REFRESH_TOKEN_SECRET;
    if (!refreshSecret) {
      throw new Error('REFRESH_TOKEN_SECRET must be set');
    }

    const decoded = jwt.verify(
      refreshToken,
      refreshSecret
    ) as { userId: string };

    const user = await prisma.user.findUnique({
      where: { id: decoded.userId }
    });

    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET must be set');
    }

    const newToken = jwt.sign(
      { userId: user.id },
      jwtSecret,
      { expiresIn: '15m' }
    );

    res.json({
      success: true,
      token: newToken
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});

// Logout Endpoint
router.post('/logout', (req: Request, res: Response) => {
  // In a stateless JWT system, logout is handled client-side
  // But we can log it for audit purposes
  res.json({ success: true, message: 'Logged out' });
});

// Verify Token
router.get('/verify', (req: Request, res: Response) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ error: 'No token' });
    }

    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET must be set');
    }

    jwt.verify(token, jwtSecret);

    res.json({ valid: true });
  } catch (error) {
    res.status(401).json({ valid: false, error: 'Invalid token' });
  }
});

export default router;
