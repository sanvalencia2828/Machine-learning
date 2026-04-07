# 🚀 Plan de Implementación Profesional: 0 a PRO
**Guía detallada para mejorar tu arquitectura en 2-4 semanas**

---

## FASE 1: LOGGING CENTRALIZADO (Día 1-2)

### Paso 1.1: Instalar dependencias
```bash
cd backend
npm install winston winston-daily-rotate-file cls-rtracer axios-tracer
npm install --save-dev @types/express @types/node @types/winston
```

### Paso 1.2: Crear logger
```typescript
// src/lib/logger.ts
import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import path from 'path';

const logsDir = path.join(process.cwd(), 'logs');

// Configurar formato
const combinedFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS Z' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.metadata({
    fillExcept: ['message', 'level', 'timestamp', 'label']
  })
);

const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  combinedFormat,
  winston.format.printf(({ timestamp, level, message, metadata }) => {
    const meta = Object.keys(metadata).length > 0 
      ? `\n  ${JSON.stringify(metadata, null, 2)}` 
      : '';
    return `${timestamp} [${level}]: ${message}${meta}`;
  })
);

const jsonFormat = winston.format.combine(
  combinedFormat,
  winston.format.json()
);

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: jsonFormat,
  transports: [
    // Console output
    new winston.transports.Console({
      format: consoleFormat
    }),

    // Error logs
    new DailyRotateFile({
      filename: path.join(logsDir, 'error-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '20m',
      maxFiles: '14d'
    }),

    // All logs
    new DailyRotateFile({
      filename: path.join(logsDir, 'combined-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '30d'
    })
  ],
  exceptionHandlers: [
    new DailyRotateFile({
      filename: path.join(logsDir, 'exceptions-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d'
    })
  ]
});

// Hacer disponible globalmente
if (process.env.NODE_ENV !== 'production') {
  global.logger = logger;
}

export default logger;
```

### Paso 1.3: Agregar middleware de correlation ID
```typescript
// src/middleware/correlation-id.middleware.ts
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

declare global {
  namespace Express {
    interface Request {
      id: string;
    }
  }
}

export const correlationIdMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = req.headers['x-correlation-id'] || uuidv4();
  req.id = correlationId as string;
  
  res.set('X-Correlation-ID', correlationId);
  
  // Agregar al logger
  logger.defaultMeta = { correlationId };
  
  next();
};
```

### Paso 1.4: Agregar logging middleware
```typescript
// src/middleware/logging.middleware.ts
import { Request, Response, NextFunction } from 'express';
import logger from '../lib/logger';

interface ResponseMetrics {
  statusCode: number;
  duration: number;
  contentLength: number;
}

export const loggingMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const startTime = Date.now();
  const originalJson = res.json.bind(res);

  res.json = function(data: any) {
    const duration = Date.now() - startTime;
    const contentLength = JSON.stringify(data).length;

    const metrics: ResponseMetrics = {
      statusCode: res.statusCode,
      duration,
      contentLength
    };

    const logLevel = res.statusCode >= 400 ? 'warn' : 'info';
    
    logger[logLevel as keyof typeof logger](`${req.method} ${req.originalUrl}`, {
      method: req.method,
      path: req.path,
      query: req.query,
      ...metrics,
      userId: (req as any).user?.id,
      ip: req.ip,
      userAgent: req.get('user-agent')?.substring(0, 100)
    });

    return originalJson(data);
  };

  next();
};
```

### Paso 1.5: Incorporar en index.ts
```typescript
// src/index.ts - Agregar esto después de helmet/cors

import { correlationIdMiddleware } from './middleware/correlation-id.middleware';
import { loggingMiddleware } from './middleware/logging.middleware';

app.use(correlationIdMiddleware);
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));
app.use(loggingMiddleware);
app.use(morgan('combined')); // Puedes eliminar después
```

---

## FASE 2: ERROR HANDLING CENTRALIZADO (Día 2-3)

### Paso 2.1: Crear tipos de error
```typescript
// src/types/errors.ts
export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  BAD_REQUEST = 'BAD_REQUEST'
}

export interface ApiError {
  code: ErrorCode;
  message: string;
  statusCode: number;
  details?: Record<string, any>;
  timestamp: string;
  correlationId?.string;
}

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: ErrorCode;
  public readonly details?: Record<string, any>;

  constructor(
    code: ErrorCode,
    message: string,
    statusCode: number,
    details?: Record<string, any>
  ) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;

    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(ErrorCode.VALIDATION_ERROR, message, 400, details);
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required') {
    super(ErrorCode.AUTHENTICATION_ERROR, message, 401);
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = 'Insufficient permissions') {
    super(ErrorCode.AUTHORIZATION_ERROR, message, 403);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id?: string) {
    const message = id 
      ? `${resource} with id '${id}' not found`
      : `${resource} not found`;
    super(ErrorCode.NOT_FOUND, message, 404);
  }
}

export class ConflictError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(ErrorCode.CONFLICT, message, 409, details);
  }
}
```

### Paso 2.2: Crear middleware de error
```typescript
// src/middleware/error-handler.middleware.ts
import { Request, Response, NextFunction } from 'express';
import logger from '../lib/logger';
import { AppError, ErrorCode } from '../types/errors';

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
  meta: {
    timestamp: string;
    correlationId: string;
    path: string;
    method: string;
  };
}

export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = req.id || 'unknown';
  const timestamp = new Date().toISOString();

  // Si es error de Prisma
  if (error.name === 'PrismaClientKnownRequestError') {
    logger.error('Database error', {
      correlationId,
      error: error.message,
      code: (error as any).code
    });

    const response: ErrorResponse = {
      code: ErrorCode.DATABASE_ERROR,
      message: 'Database operation failed',
      meta: {
        timestamp,
        correlationId,
        path: req.path,
        method: req.method
      }
    };

    return res.status(500).json(response);
  }

  // Si es AppError
  if (error instanceof AppError) {
    logger.warn('Application error', {
      code: error.code,
      statusCode: error.statusCode,
      message: error.message,
      details: error.details,
      path: req.path,
      method: req.method,
      correlationId
    });

    const response: ErrorResponse = {
      code: error.code,
      message: error.message,
      details: error.details,
      meta: {
        timestamp,
        correlationId,
        path: req.path,
        method: req.method
      }
    };

    return res.status(error.statusCode).json(response);
  }

  // Unexpected error
  logger.error('Unhandled error', {
    message: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    correlationId,
    userId: (req as any).user?.id
  });

  const response: ErrorResponse = {
    code: ErrorCode.INTERNAL_ERROR,
    message: 'An unexpected error occurred',
    meta: {
      timestamp,
      correlationId,
      path: req.path,
      method: req.method
    }
  };

  res.status(500).json(response);
};

// Capturar rutas no encontradas
export const notFoundHandler = (
  req: Request,
  res: Response
) => {
  const response: ErrorResponse = {
    code: ErrorCode.NOT_FOUND,
    message: `Route ${req.method} ${req.path} not found`,
    meta: {
      timestamp: new Date().toISOString(),
      correlationId: req.id,
      path: req.path,
      method: req.method
    }
  };

  res.status(404).json(response);
};

// Convertir excepciones no capturadas en AppError
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
```

### Paso 2.3: Actualizar index.ts
```typescript
// src/index.ts - Al final del archivo, antes de listen

import { errorHandler, notFoundHandler } from './middleware/error-handler.middleware';

// ... todas tus rutas aquí

// Handler para rutas no encontradas
app.use(notFoundHandler);

// Error handler (DEBE ser el último middleware)
app.use(errorHandler);

// Manejo de promesas no capturadas
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

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`, {
    environment: process.env.NODE_ENV,
    nodeVersion: process.version
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});
```

---

## FASE 3: VALIDACIÓN CON ZOD (Día 3-4)

### Paso 3.1: Instalar Zod
```bash
npm install zod
```

### Paso 3.2: Crear esquemas
```typescript
// src/schemas/auth.schema.ts
import { z } from 'zod';

export const signUpSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  password: z
    .string()
    .min(12, 'Password must be at least 12 characters')
    .regex(/[A-Z]/, 'Password must contain uppercase letter')
    .regex(/[a-z]/, 'Password must contain lowercase letter')
    .regex(/[0-9]/, 'Password must contain number')
    .regex(/[!@#$%^&*]/, 'Password must contain special character'),
  passwordConfirm: z.string()
}).refine((data) => data.password === data.passwordConfirm, {
  message: 'Passwords do not match',
  path: ['passwordConfirm']
});

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required')
});

export const refreshTokenSchema = z.object({
  refreshToken: z.string().min(1, 'Refresh token is required')
});

export type SignUpInput = z.infer<typeof signUpSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
```

```typescript
// src/schemas/course.schema.ts
import { z } from 'zod';

export const createCourseSchema = z.object({
  titleEs: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters'),
  titleEn: z.string()
    .min(3)
    .max(200),
  descriptionEs: z.string().max(2000).optional(),
  descriptionEn: z.string().max(2000).optional(),
  price: z.number().min(0).max(10000),
  currency: z.enum(['USD', 'EUR', 'ARS']).default('USD'),
  collaborationStatus: z.enum(['open', 'closed', 'archived']).default('open')
});

export const updateCourseSchema = createCourseSchema.partial();

export type CreateCourseInput = z.infer<typeof createCourseSchema>;
export type UpdateCourseInput = z.infer<typeof updateCourseSchema>;
```

### Paso 3.3: Crear middleware de validación
```typescript
// src/middleware/validate.middleware.ts
import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { ValidationError as AppValidationError } from '../types/errors';

export const validate = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Validar body
      if (req.body) {
        req.body = await schema.parseAsync(req.body);
      }

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const details = error.errors.reduce((acc, err) => {
          const path = err.path.join('.');
          acc[path] = err.message;
          return acc;
        }, {} as Record<string, string>);

        throw new AppValidationError(
          'Validation failed',
          details
        );
      }

      next(error);
    }
  };
};

export const validateQuery = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      req.query = await schema.parseAsync(req.query);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const details = error.errors.reduce((acc, err) => {
          acc[err.path.join('.')] = err.message;
          return acc;
        }, {} as Record<string, string>);

        throw new AppValidationError(
          'Query validation failed',
          details
        );
      }

      next(error);
    }
  };
};
```

### Paso 3.4: Usar en rutas
```typescript
// src/routes/auth.routes.ts
import { validate } from '../middleware/validate.middleware';
import { signUpSchema, loginSchema } from '../schemas/auth.schema';
import { asyncHandler } from '../middleware/error-handler.middleware';

router.post('/signup', 
  validate(signUpSchema),
  asyncHandler(authController.signup)
);

router.post('/login',
  validate(loginSchema),
  asyncHandler(authController.login)
);
```

---

## FASE 4: HEALTH CHECKS & READINESS (Día 4)

### Paso 4.1: Crear health check service
```typescript
// src/services/health.service.ts
import { prisma } from '../lib/prisma';
import { redis } from '../lib/redis';
import logger from '../lib/logger';

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  database: {
    status: 'up' | 'down';
    latency?: number;
    error?: string;
  };
  redis?: {
    status: 'up' | 'down';
    latency?: number;
    error?: string;
  };
  checks: {
    name: string;
    status: 'pass' | 'fail';
    latency: number;
  }[];
}

export const healthService = {
  async check(): Promise<HealthStatus> {
    const startTime = Date.now();
    const checks: HealthStatus['checks'] = [];
    let overallStatus: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';

    // Check database
    try {
      const dbStart = Date.now();
      await prisma.$queryRaw`SELECT 1`;
      const dbLatency = Date.now() - dbStart;

      checks.push({
        name: 'database',
        status: 'pass',
        latency: dbLatency
      });
    } catch (error) {
      logger.error('Database health check failed', { error: String(error) });
      checks.push({
        name: 'database',
        status: 'fail',
        latency: 0
      });
      overallStatus = 'unhealthy';
    }

    // Check Redis (if configured)
    if (process.env.REDIS_HOST) {
      try {
        const redisStart = Date.now();
        await redis.ping();
        const redisLatency = Date.now() - redisStart;

        checks.push({
          name: 'redis',
          status: 'pass',
          latency: redisLatency
        });
      } catch (error) {
        logger.warn('Redis health check failed', { error: String(error) });
        checks.push({
          name: 'redis',
          status: 'fail',
          latency: 0
        });
        overallStatus = 'degraded';
      }
    }

    return {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      database: {
        status: checks.find(c => c.name === 'database')?.status === 'pass' ? 'up' : 'down'
      },
      checks
    };
  }
};
```

### Paso 4.2: Agregar endpoints
```typescript
// src/routes/health.routes.ts
import { Router } from 'express';
import { healthService } from '../services/health.service';
import { asyncHandler } from '../middleware/error-handler.middleware';

const router = Router();

// Simple liveness probe
router.get('/', asyncHandler(async (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
}));

// Detailed readiness probe
router.get('/ready', asyncHandler(async (req, res) => {
  const health = await healthService.check();
  const statusCode = health.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(health);
}));

// Kubernetes liveness probe
router.get('/live', asyncHandler(async (req, res) => {
  res.json({ status: 'alive' });
}));

export default router;
```

---

## FASE 5: RATE LIMITING INTELIGENTE (Día 5)

### Paso 5.1: Configurar rate limiters específicos
```typescript
// src/middleware/rate-limit.middleware.ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redis } from '../lib/redis';
import logger from '../lib/logger';

// Rate limiter genérico
export const createRateLimiter = (
  windowMs: number,
  max: number,
  message: string
) => {
  const store = redis 
    ? new RedisStore({
        client: redis,
        prefix: 'rate-limit:',
        expiry: windowMs / 1000,
        sendCommand: async (command: string, args: string[]) => {
          return redis[command as keyof typeof redis](...args);
        }
      })
    : undefined;

  return rateLimit({
    store,
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
    onLimitReached: (req, res, options) => {
      logger.warn('Rate limit reached', {
        ip: req.ip,
        path: req.path,
        userId: (req as any).user?.id,
        limit: options.max
      });
    }
  });
};

// Limiters específicos
export const generalLimiter = createRateLimiter(
  15 * 60 * 1000, // 15 minutos
  100,
  'Too many requests, please try again later.'
);

export const authLimiter = createRateLimiter(
  15 * 60 * 1000, // 15 minutos
  5, // Máximo 5 intentos
  'Too many login attempts, please try again after 15 minutes.'
);

export const apiLimiter = createRateLimiter(
  60 * 1000, // 1 minuto
  30, // 30 requests per minute
  'API rate limit exceeded.'
);

export const uploadLimiter = createRateLimiter(
  24 * 60 * 60 * 1000, // 24 horas
  50, // 50 uploads per day
  'Daily upload limit exceeded.'
);

export const strictLimiter = createRateLimiter(
  60 * 60 * 1000, // 1 hora
  10, // 10 requests per hour
  'Rate limit exceeded.'
);
```

### Paso 5.2: Usar en rutas
```typescript
// src/index.ts

import { 
  generalLimiter, 
  authLimiter, 
  apiLimiter 
} from './middleware/rate-limit.middleware';

// Aplicar general limiter a todas las rutas API
app.use('/api/', generalLimiter);

// Limiters específicos por ruta
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
app.use('/api/auth/forgot-password', authLimiter);
app.use('/api/upload', uploadLimiter);
```

---

## 🎯 Verificación de Implementación

### Pruebas locales
```bash
# 1. Verificar logs
tail -f logs/combined-*.log

# 2. Probar error handling
curl -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"invalid": "data"}'

# 3. Probar health checks
curl http://localhost:3000/health
curl http://localhost:3000/health/ready

# 4. Probar rate limiting
for i in {1..10}; do curl http://localhost:3000/api/auth/login; done

# 5. Probar validación
curl -X POST http://localhost:3000/api/courses \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"titleEs": "ab"}'  # Menos de 3 caracteres
```

---

## 📋 Resumen de Cambios

| Componente | Cambio | Beneficio |
|-----------|--------|----------|
| Logger | Winston + DailyRotate | Logs estructurados, fácil auditoría |
| Error Handling | AppError centralizado | Consistencia en respuestas |
| Validación | Zod schemas | Type-safe, validación declarativa |
| Health Checks | /health y /health/ready | Kubernetes-ready |
| Rate Limiting | Inteligente por endpoint | Protección contra abuso |

---

## Tiempo Estimado
- **Fase 1**: 2-3 horas
- **Fase 2**: 2-3 horas  
- **Fase 3**: 2-3 horas
- **Fase 4**: 1-2 horas
- **Fase 5**: 1-2 horas

**Total: 8-13 horas = 1-2 días de trabajo**

---

## ¿Qué sigue?

Después de implementar esto:

1. **Agregar Testing** → Jest + Supertest
2. **Documentación API** → Swagger/OpenAPI
3. **Caching** → Redis integration
4. **Database Optimization** → Connection pooling + Índices
5. **Monitoreo** → Prometheus + Grafana

¿Quieres que te ayude a implementar alguna phase en particular?
