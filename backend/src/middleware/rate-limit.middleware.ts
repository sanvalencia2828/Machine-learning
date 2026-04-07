import rateLimit from 'express-rate-limit';
import logger from '../lib/logger';

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
    skip: (req) => {
      // Skip rate limiting para admin
      return (req as any).user?.roles?.includes('admin');
    },
    keyGenerator: (req) => {
      // Usar user ID si está autenticado, sino IP
      return (req as any).user?.id || req.ip || 'unknown';
    },
    handler: (req: any, res: any, _next: any, options: any) => {
      logger.warn(`Rate limit reached: ${name}`, {
        ip: req.ip,
        path: req.path,
        userId: (req as any).user?.id,
        limit: options?.max
      });
      // Send standard 429 response
      try {
        res.status(429).json({ error: message });
      } catch (err) {
        // fallback: end response
        try { res.statusCode = 429; res.end(); } catch (e) { /* ignore */ }
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
