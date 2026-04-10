import express, { Request, Response } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import rTracer from 'cls-rtracer';
import { config } from 'dotenv';

import logger from './lib/logger.js';
import { correlationIdMiddleware } from './middleware/correlation-id.middleware.js';
import { loggingMiddleware } from './middleware/logging.middleware.js';
import { errorHandler, notFoundHandler } from './middleware/error-handler.middleware.js';
import { generalLimiter, authLimiter } from './middleware/rate-limit.middleware.js';
import healthRouter from './routes/health.routes.js';
import { asyncHandler } from './utils/async-handler.js';

import authRoutes from './routes/auth.routes.js';
import modulesRoutes from './routes/modules.routes.js';

config();

const app = express();
const PORT = process.env.PORT || 3001;

logger.info('Starting application', {
  environment: process.env.NODE_ENV || 'development',
  nodeVersion: process.version
});

// ============ SECURITY MIDDLEWARE ============
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:']
    }
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
  frameguard: { action: 'deny' },
  noSniff: true,
  xssFilter: true
}));

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Correlation-ID'],
  maxAge: 86400
}));

// ============ COMPRESSION ============
app.use(compression());

// ============ REQUEST PARSING ============
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));

// ============ REQUEST TRACKING & LOGGING ============
app.use(correlationIdMiddleware);
app.use(loggingMiddleware);

// ============ ROUTE PREFIX ============
// En Vercel, routePrefix: "/api" ya antepone /api a todas las rutas,
// asi que internamente montamos todo sin prefijo.
// En local, necesitamos el prefijo /api manualmente.
const prefix = process.env.VERCEL ? '' : '/api';

// ============ RATE LIMITING ============
app.use(`${prefix}/`, generalLimiter);
app.use(`${prefix}/auth/login`, authLimiter);
app.use(`${prefix}/auth/register`, authLimiter);
app.use(`${prefix}/auth/forgot-password`, authLimiter);

// ============ HEALTH CHECK ROUTES ============
app.use('/health', healthRouter);

// ============ STATUS ENDPOINT ============
app.get('/status', asyncHandler(async (_req: Request, res: Response) => {
  res.json({
    status: 'running',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    uptime: process.uptime()
  });
}));

// ============ TEST ENDPOINT ============
app.get(`${prefix}/test`, asyncHandler(async (req: Request, res: Response) => {
  logger.info('Test endpoint called', {
    path: req.path,
    correlationId: rTracer.id()
  });
  res.json({
    message: 'API is working!',
    correlationId: rTracer.id(),
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
    features: {
      logging: 'enabled',
      errorHandling: 'enabled',
      validation: 'enabled',
      rateLimiting: 'enabled',
      healthChecks: 'enabled'
    }
  });
}));

// ============ APPLICATION ROUTES ============
app.use(`${prefix}/auth`, authRoutes);
app.use(`${prefix}/modules`, modulesRoutes);

// ============ 404 & ERROR HANDLING ============
app.use(notFoundHandler);
app.use(errorHandler);

// ============ PROCESS ERROR HANDLERS ============
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection', {
    reason: String(reason),
    promise: String(promise)
  });
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', {
    message: error.message,
    stack: error.stack
  });
  process.exit(1);
});

// ============ START SERVER ============
const server = app.listen(PORT, () => {
  logger.info(`🚀 Server running on port ${PORT}`, {
    environment: process.env.NODE_ENV,
    nodeVersion: process.version,
    url: `http://localhost:${PORT}`,
    features: ['Logging', 'Error Handling', 'Validation', 'Rate Limiting', 'Health Checks']
  });
});

// ============ GRACEFUL SHUTDOWN ============
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('🛑 Server closed');
    process.exit(0);
  });
});

export default app;
