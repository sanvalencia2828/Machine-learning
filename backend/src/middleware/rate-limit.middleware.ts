import rateLimit from 'express-rate-limit';
import logger from '../lib/logger.js';
import { Request, Response, NextFunction } from 'express';

/**
 * Crear un rate limiter personalizado
 */
export const createRateLimiter = (
  windowMs: number,
  max: number,
  message: string,
  name: string
) => {
  return rateLimit({
    windowMs,
    max,
    message,
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req: Request) => {
      // Skip rate limiting para admin
      const u = req as Request & { user?: { roles?: string[] } };
      return u.user?.roles?.includes('admin') ?? false;
    },
    keyGenerator: (req: Request) => {
      // Usar user ID si está autenticado, sino IP
      const u = req as Request & { user?: { id?: string } };
      return u.user?.id || req.ip || 'unknown';
    },
    handler: (req: Request, res: Response, _next: NextFunction, options: unknown) => {
      const u = req as Request & { user?: { id?: string } };
      const opt = options as { max?: number | ((...args: unknown[]) => number) } | undefined;
      const maxVal = opt && typeof opt.max === 'number' ? opt.max : undefined;

      logger.warn(`Rate limit reached: ${name}`, {
        ip: req.ip,
        path: req.path,
        userId: u.user?.id,
        limit: maxVal
      });
      try {
        res.status(429).json({ error: message });
      } catch {
        try { res.statusCode = 429; res.end(); } catch { /* ignore */ }
      }
    }
  });
};

// ============ RATE LIMITERS POR TIPO ============

// General limiter (100 requests per 15 minutes)
export const generalLimiter = createRateLimiter(
  15 * 60 * 1000,
  100,
  'Too many requests, please try again later.',
  'general'
);

// Auth limiter (5 attempts per 15 minutes)
export const authLimiter = createRateLimiter(
  15 * 60 * 1000,
  5,
  'Too many login attempts, please try again after 15 minutes.',
  'auth'
);

// API limiter (30 requests per minute)
export const apiLimiter = createRateLimiter(
  60 * 1000,
  30,
  'API rate limit exceeded.',
  'api'
);

// Upload limiter (50 uploads per 24 hours)
export const uploadLimiter = createRateLimiter(
  24 * 60 * 60 * 1000,
  50,
  'Daily upload limit exceeded.',
  'upload'
);

// Strict limiter (10 requests per hour)
export const strictLimiter = createRateLimiter(
  60 * 60 * 1000,
  10,
  'Rate limit exceeded.',
  'strict'
);
