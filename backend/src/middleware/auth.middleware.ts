import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthPayload {
  userId: string;
  email: string;
  plan: string;
}

export interface AuthRequest extends Request {
  user?: AuthPayload;
}

export function authMiddleware(req: AuthRequest, res: Response, next: NextFunction): void {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Token requerido' });
    return;
  }

  const token = header.slice(7);
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET || 'dev-secret') as AuthPayload;
    req.user = payload;
    next();
  } catch {
    res.status(401).json({ error: 'Token invalido o expirado' });
  }
}

const TIER_HIERARCHY: Record<string, number> = {
  FREE: 0,
  BASICO: 1,
  AVANZADO: 2,
  PREMIUM: 3,
};

export function requirePlan(minPlan: string) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    const userLevel = TIER_HIERARCHY[req.user?.plan || 'FREE'] ?? 0;
    const requiredLevel = TIER_HIERARCHY[minPlan] ?? 0;

    if (userLevel < requiredLevel) {
      res.status(403).json({
        error: 'Plan insuficiente',
        required: minPlan,
        current: req.user?.plan || 'FREE',
      });
      return;
    }
    next();
  };
}
