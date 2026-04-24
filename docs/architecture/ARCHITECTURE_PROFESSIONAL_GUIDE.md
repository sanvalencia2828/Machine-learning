# 🏗️ Arquitectura Profesional: De 0 a PRO

**ML Course Platform - Guía Integral de Arquitectura y Diseño**

---

## 📊 Diagrama de Arquitectura Actual → Mejorada

### Estado Actual (Básico)
```
┌─────────────┐
│   Frontend  │  (Next.js - básico)
│  (3001)     │
└──────┬──────┘
       │ HTTP
┌──────▼──────────────────────────────┐
│      Backend (Express)               │
│  - /api/auth                         │
│  - /api/courses                      │
│  - /api/users                        │
│  - Rate limiting básico              │
└──────┬──────────────────────────────┘
       │ SQL
┌──────▼──────────────────────────────┐
│   PostgreSQL (sin pooling)           │
│   - Users                            │
│   - Courses                          │
│   - Roles/Permissions                │
└──────────────────────────────────────┘
```

### Arquitectura Profesional (Pro)
```
┌────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
├────────────┬────────────────────────────┬───────────────────┤
│  Web SPA   │  Mobile (React Native)     │  CLI / Webhooks   │
│ (Next.js)  │  (Optional)                │                   │
└──────┬─────┴────────────┬───────────────┴──────────┬────────┘
       │                  │                          │
       │  HTTPS+TLS       │ REST/GraphQL             │ Webhooks
       │                  │                          │
┌──────▼──────────────────▼──────────────────────────▼──────────┐
│                    API GATEWAY LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  • Rate Limiting (per user, per IP, per endpoint)        │ │
│  │  • Request/Response Validation & Transformation          │ │
│  │  • API Versioning (v1, v2, ...)                          │ │
│  │  • Request Correlation IDs                               │ │
│  │  • Load Balancing (round-robin, least-conn)              │ │
│  │  • Circuit Breaker Pattern                               │ │
│  │  • OpenAPI/Swagger Documentation                         │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────┬────────────────────────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────────────────────┐
│               BACKEND LAYER (Node.js/Express)                │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─ AUTH SERVICE ┐  ┌─ COURSE SERVICE ┐  ┌─ USER SERVICE ┐  │
│  │ • Passport    │  │ • Content Logic │  │ • Profile Mgmt │ │
│  │ • JWT Token   │  │ • Publishing    │  │ • Roles/Perms  │ │
│  │ • OAuth 2.0   │  │ • Translations  │  │ • Audit Trail  │ │
│  │ • RBAC/ABAC   │  │ • Variants      │  │ • Preferences  │ │
│  └────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CROSS-CUTTING CONCERNS                                  │ │
│  │  • Structured Logging (Winston, Pino)                     │ │
│  │  • Request/Response Interceptors                          │ │
│  │  • Error Handling (Error Codes, Stack Traces)             │ │
│  │  • Monitoring/Observability (OpenTelemetry)               │ │
│  │  • Dependency Injection                                   │ │
│  │  • Transaction Management                                 │ │
│  █  • Cache Layer (Redis)                                    │ │
│  │  • Feature Flags (LaunchDarkly, etc)                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
└──────┬───────────┬──────────────────┬────────────────────────┘
       │           │                  │
       │           │                  │
┌──────▼─┐  ┌──────▼──────┐    ┌─────▼──────┐
│ Primary│  │   Redis     │    │   S3/Blob  │
│Postgres│  │  (Cache)    │    │  Storage   │
│        │  │             │    │            │
│Pooling │  └─────────────┘    └────────────┘
│PgBouncer
└────────┘

       ┌──────────────────────┐
       │  Background Jobs     │
       │  (Bull, BullMQ)      │
       │  • Email             │
       │  • ETL Processing    │
       │  • Notifications     │
       │  • Analytics         │
       └──────────────────────┘
```

---

## 🎯 Pilares de Arquitectura Profesional

### 1️⃣ **SEGURIDAD** (Security First)

#### Baseline
```typescript
// ❌ Current Implementation (Basic)
app.use(helmet());
app.use(cors({...}));
const limiter = rateLimit({...});
```

#### 🚀 Profesional
```typescript
// ✅ Comprehensive Security Layer

// 1. Helmet configuración exhaustiva
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "trusted-cdn.com"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.example.com"],
      fontSrc: ["'self'", "data:", "https://fonts.googleapis.com"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"],
      upgradeInsecureRequests: []
    }
  },
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: true,
  crossOriginResourcePolicy: { policy: "cross-origin" },
  dnsPrefetchControl: { allow: false },
  frameguard: { action: 'deny' },
  hidePoweredBy: true,
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  ieNoOpen: true,
  noSniff: true,
  originAgentCluster: true,
  permittedCrossDomainPolicies: false,
  referrerPolicy: { policy: "no-referrer" },
  xssFilter: true,
  expectCT: { max_age: 86400, enforce: true }
}));

// 2. CORS inteligente (por origen)
const corsOptions: CorsOptions = {
  origin: (origin, callback) => {
    const whitelist = [
      process.env.FRONTEND_URL,
      process.env.ADMIN_URL,
      'https://app.example.com',
      'https://admin.example.com'
    ];
    
    if (!origin || whitelist.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('CORS policy violation'), false);
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID', 'X-Correlation-ID'],
  exposedHeaders: ['X-Request-ID', 'X-RateLimit-Limit', 'X-RateLimit-Remaining'],
  maxAge: 86400 // 24 hours
};
app.use(cors(corsOptions));

// 3. Rate Limiting por tipo de endpoint
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 min
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => req.user?.roles.includes('admin'),
  keyGenerator: (req) => {
    return (req.user?.id || req.ip) || 'unknown';
  }
});

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // Estricto para auth
  skipSuccessfulRequests: true,
  message: 'Demasiados intentos de login. Intenta más tarde.'
});

const uploadLimiter = rateLimit({
  windowMs: 24 * 60 * 60 * 1000, // 24 horas
  max: 50, // Por usuario
  message: 'Has alcanzado el límite de carga diaria'
});

app.use('/api/', generalLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
app.use('/api/upload', uploadLimiter);

// 4. SQL Injection Prevention (Prisma ORM)
// Prisma usa query parameterization automáticamente

// 5. XSS Prevention
import xss from 'xss-clean';
app.use(xss());

// 6. Data Sanitization
import mongoSanitize from 'mongo-sanitize'; // también funciona para PostgreSQL
app.use(mongoSanitize());

// 7. HTTPS redirection
if (process.env.NODE_ENV === 'production') {
  app.use((req, res, next) => {
    if (req.header('x-forwarded-proto') !== 'https') {
      res.redirect(`https://${req.header('host')}${req.url}`);
    } else {
      next();
    }
  });
}
```

### 2️⃣ **STRUCTURED LOGGING & OBSERVABILITY**

#### Baseline
```typescript
app.use(morgan('combined')); // Solo HTTP access logs
```

#### 🚀 Profesional
```typescript
// src/lib/logger.ts
import winston from 'winston';
import rTracer from 'cls-rtracer';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      const correlationId = rTracer.id();
      return JSON.stringify({
        timestamp,
        level: level.toUpperCase(),
        correlationId,
        message,
        ...meta
      });
    })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/all.log' }),
    process.env.NODE_ENV === 'production' &&
      new winston.transports.File({
        filename: 'logs/analytics.log',
        format: winston.format.json()
      })
  ].filter(Boolean),
  exceptionHandlers: [
    new winston.transports.File({ filename: 'logs/exceptions.log' })
  ],
  rejectionHandlers: [
    new winston.transports.File({ filename: 'logs/rejections.log' })
  ]
});

// src/middleware/logging.middleware.ts
export const loggingMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const originalJson = res.json.bind(res);
  const originalSend = res.send.bind(res);

  res.json = function(body: any) {
    const duration = Date.now() - start;
    logger.info('API Request', {
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration,
      userId: req.user?.id,
      ip: req.ip,
      userAgent: req.get('user-agent'),
      responseSize: JSON.stringify(body).length,
      query: req.query,
    });
    return originalJson(body);
  };

  res.send = function(body: any) {
    const duration = Date.now() - start;
    logger.info('API Request', {
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration,
      responseSize: typeof body === 'string' ? body.length : 0,
    });
    return originalSend(body);
  };

  next();
};
```

### 3️⃣ **VALIDACIÓN & REQUEST/RESPONSE STANDARDIZATION**

#### Baseline
```typescript
// Mentioned but not implemented
```

#### 🚀 Profesional
```typescript
// src/types/api-response.ts
export enum ResponseCode {
  SUCCESS = 'SUCCESS',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  RATE_LIMIT = 'RATE_LIMIT',
  FORBIDDEN = 'FORBIDDEN'
}

export type ApiResponse<T> = {
  code: ResponseCode;
  message: string;
  data?: T;
  errors?: ValidationError[];
  meta?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
};

export type ValidationError = {
  field: string;
  message: string;
  code: string; // 'REQUIRED', 'INVALID_FORMAT', etc.
};

// src/lib/validators.ts
import { z } from 'zod';

export const emailSchema = z.string().email().toLowerCase();
export const passwordSchema = z
  .string()
  .min(12, 'Password must be at least 12 characters')
  .regex(/[A-Z]/, 'Password must contain uppercase letter')
  .regex(/[a-z]/, 'Password must contain lowercase letter')
  .regex(/[0-9]/, 'Password must contain number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain special character');

export const createCourseSchema = z.object({
  titleEs: z.string().min(3).max(200),
  titleEn: z.string().min(3).max(200),
  descriptionEs: z.string().optional(),
  descriptionEn: z.string().optional(),
  price: z.number().min(0).max(10000),
  currency: z.enum(['USD', 'EUR', 'ARS']).default('USD'),
  collaborationStatus: z.enum(['open', 'closed', 'archived']).default('open')
});

// src/middleware/validation.middleware.ts
export const validateRequest = (schema: z.ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = await schema.parseAsync(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        const validationErrors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
          code: err.code
        }));
        
        return res.status(400).json({
          code: ResponseCode.VALIDATION_ERROR,
          message: 'Validation failed',
          errors: validationErrors,
          meta: {
            timestamp: new Date().toISOString(),
            requestId: rTracer.id(),
            version: '1.0'
          }
        } as ApiResponse<null>);
      }
      next(error);
    }
  };
};

// Uso:
router.post('/courses', 
  authMiddleware,
  validateRequest(createCourseSchema),
  coursesController.create
);
```

### 4️⃣ **ERROR HANDLING CENTRALIZADO**

#### Baseline
```typescript
try {
  // query
} catch (error) {
  console.error('Auth error:', error);
  res.status(401).json({ error: 'Invalid token' });
}
```

#### 🚀 Profesional
```typescript
// src/types/app-error.ts
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: ResponseCode,
    message: string,
    public details?: Record<string, any>,
    public isOperational: boolean = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public errors: ValidationError[]) {
    super(400, ResponseCode.VALIDATION_ERROR, message);
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required') {
    super(401, ResponseCode.AUTH_ERROR, message);
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = 'Insufficient permissions') {
    super(403, ResponseCode.FORBIDDEN, message);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(404, ResponseCode.NOT_FOUND, `${resource} with id ${id} not found`);
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(409, ResponseCode.CONFLICT, message);
  }
}

// src/middleware/error-handler.middleware.ts
export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const requestId = rTracer.id();
  const timestamp = new Date().toISOString();

  if (error instanceof AppError) {
    logger.warn('Application Error', {
      code: error.code,
      statusCode: error.statusCode,
      message: error.message,
      requestId,
      path: req.path,
      method: req.method,
      userId: req.user?.id
    });

    return res.status(error.statusCode).json({
      code: error.code,
      message: error.message,
      details: error.details,
      meta: {
        timestamp,
        requestId,
        version: '1.0'
      }
    } as ApiResponse<null>);
  }

  // Unexpected errors
  logger.error('Unhandled Error', {
    message: error.message,
    stack: error.stack,
    requestId,
    path: req.path,
    method: req.method,
    userId: req.user?.id,
    headers: req.headers
  });

  res.status(500).json({
    code: ResponseCode.INTERNAL_ERROR,
    message: 'Internal server error',
    meta: {
      timestamp,
      requestId,
      version: '1.0'
    }
  } as ApiResponse<null>);
};

// Registro de error handler como último middleware
app.use(errorHandler);
```

### 5️⃣ **DATABASE LAYER - CONNECTION POOLING & TRANSACTIONS**

#### Baseline
```typescript
// No connection pooling visible, Prisma por defecto (limitado)
```

#### 🚀 Profesional
```typescript
// src/lib/db.ts
import { PrismaClient } from '@prisma/client';

// Configurar Prisma con connection pool
export const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL // debe incluir pool config
    }
  },
  log: [
    { emit: 'stdout', level: 'query' },
    { emit: 'stdout', level: 'error' },
    { emit: 'stdout', level: 'warn' }
  ]
});

// src/lib/pgbouncer-config.txt (en producción)
[databases]
postgres = host=rds-instance.region.rds.amazonaws.com port=5432 user=admin password=***

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3

# .env.local
DATABASE_URL="postgresql://user:pass@pgbouncer-host:6432/db_name?schema=public&connection_limit=10"

// src/services/transaction.service.ts
export const transactionService = {
  async runInTransaction<T>(
    callback: (tx: typeof prisma) => Promise<T>,
    options?: { timeout?: number; isolationLevel?: string }
  ): Promise<T> {
    return prisma.$transaction(
      async (tx) => {
        return callback(tx);
      },
      {
        timeout: options?.timeout || 10000,
        isolationLevel: options?.isolationLevel as any || 'Serializable'
      }
    );
  }
};

// Producto service con transacción
export const courseService = {
  async createCourseWithChapters(
    createCourseDto: CreateCourseDto,
    chapters: CreateChapterDto[]
  ) {
    return transactionService.runInTransaction(async (tx) => {
      // Crear curso
      const course = await tx.course.create({
        data: {
          titleEs: createCourseDto.titleEs,
          titleEn: createCourseDto.titleEn,
          createdById: createCourseDto.userId,
          price: createCourseDto.price
        }
      });

      // Crear capítulos (si falla, todo se rollback)
      const createdChapters = await tx.chapter.createMany({
        data: chapters.map((ch, idx) => ({
          titleEs: ch.titleEs,
          titleEn: ch.titleEn,
          courseId: course.id,
          order: idx + 1
        }))
      });

      return { course, chaptersCount: createdChapters.count };
    });
  }
};
```

### 6️⃣ **CACHING STRATEGY**

#### Baseline
```typescript
// No caching visible
```

#### 🚀 Profesional
```typescript
// src/lib/redis.ts
import Redis from 'ioredis';

export const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD,
  retryStrategy: (times) => Math.min(times * 50, 2000),
  maxRetriesPerRequest: null,
  enableReadyCheck: false,
  enableOfflineQueue: false,
  lazyConnect: true
});

redis.on('error', (err) => logger.error('Redis error', { error: err.message }));
redis.on('connect', () => logger.info('Redis connected'));

// src/lib/cache-decorator.ts
export const cached = (
  keyPrefix: string,
  ttl: number = 3600 // 1 hour default
) => {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;

    descriptor.value = async function(...args: any[]) {
      // Generar clave de caché
      const cacheKey = `${keyPrefix}:${JSON.stringify(args)}`;

      // Intentar obtener del caché
      const cached = await redis.get(cacheKey);
      if (cached) {
        logger.debug('Cache hit', { cacheKey });
        return JSON.parse(cached);
      }

      // Ejecutar método original
      const result = await originalMethod.apply(this, args);

      // Guardar en caché
      await redis.setex(cacheKey, ttl, JSON.stringify(result));
      logger.debug('Cache set', { cacheKey, ttl });

      return result;
    };

    return descriptor;
  };
};

// Uso en service
export const courseService = {
  @cached('courses:list', 1800)
  async getPublishedCourses(page: number = 1, limit: number = 20) {
    return prisma.course.findMany({
      where: { isPublished: true },
      skip: (page - 1) * limit,
      take: limit,
      include: { chapters: true }
    });
  },

  async updateCourse(id: string, data: UpdateCourseDto) {
    // Actualizar DB
    const course = await prisma.course.update({
      where: { id },
      data
    });

    // Invalidar caché
    await redis.del(`courses:list:*`);
    await redis.del(`course:detail:${id}`);

    return course;
  }
};
```

### 7️⃣ **API VERSIONING**

#### Baseline
```typescript
app.use('/api/auth', authRoutes);
```

#### 🚀 Profesional
```typescript
// src/routes/index.ts
import { Router } from 'express';
import { v1Router } from './v1';
import { v2Router } from './v2';

const router = Router();

// API v1 (legacy)
router.use('/v1', v1Router);

// API v2 (current)
router.use('/v2', v2Router);

// Default to latest
router.use(v2Router);

// Deprecated endpoints with warning
router.use((req, res, next) => {
  if (req.baseUrl.includes('/v1')) {
    res.set('Deprecation', 'true');
    res.set('Sunset', new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toUTCString());
    res.set('Link', '</api/v2/...>; rel="successor-version"');
  }
  next();
});

export default router;

// src/routes/v2/courses.routes.ts
export const coursesV2Router = Router();

coursesV2Router.get(
  '/courses',
  transformQueryMiddleware,
  paginationMiddleware,
  coursesController.list
);

// Ejemplo de transformación entre versiones
// En v1: ?page=1&limit=20
// En v2: ?offset=0&size=20 OR ?cursor=abc123
```

---

## 🔧 IMPLEMENTACIÓN POR CAPAS

### **Capa 1: Base de Datos (Día 1)**
```typescript
// 1. Configurar PgBouncer
// 2. Agregar índices faltantes
// 3. Implementar particionamiento (si > 100M registros)
// 4. Backup y disaster recovery

// Índices críticos
CREATE INDEX idx_users_email_status ON users(email, email_verified) WHERE NOT deleted_at;
CREATE INDEX idx_courses_published ON courses(is_published, created_at DESC) WHERE is_published;
CREATE INDEX idx_chapters_course ON chapters(course_id, "order");
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
```

### **Capa 2: Backend Core (Días 1-3)**
```
✓ Logger centralizado
✓ Error handling estandarizado
✓ Validación con Zod
✓ CORS y seguridad headers
✓ Rate limiting por endpoint
✓ Health checks y liveness probes
```

### **Capa 3: Features Principales (Días 3-7)**
```
✓ Authentication mejorada
✓ JWT con refresh tokens
✓ OAuth 2.0 PKCE flow
✓ Session management
✓ RBAC/ABAC
```

### **Capa 4: Optimización (Días 7-10)**
```
✓ Caching con Redis
✓ Connection pooling
✓ API rate limiting inteligente
✓ Request correlation IDs
✓ Distributed tracing
```

### **Capa 5: Monitoring & Observability (Días 10-14)**
```
✓ OpenTelemetry setup
✓ Prometheus metrics
✓ CloudWatch/Datadog integration
✓ Alert rules
✓ Dashboard
```

---

## 📋 Checklist de Implementación Profesional

### Sprint 1: Foundation (1 semana)
- [ ] Configurar logger centralizado
- [ ] Implementar error handling
- [ ] Agregar validación Zod
- [ ] Mejorar rate limiting
- [ ] Health checks endpoints
- [ ] Agregar estructuras de respuesta estándar

### Sprint 2: Security & Auth (1 semana)
- [ ] Implementar JWT refresh tokens
- [ ] OAuth 2.0 PKCE flow
- [ ] Session management
- [ ] Password hashing mejorado
- [ ] Email verification
- [ ] 2FA (optional)

### Sprint 3: Performance (1 semana)
- [ ] Redis caching layer
- [ ] Database indexing
- [ ] Query optimization
- [ ] Comprensión de respuestas
- [ ] Lazy loading

### Sprint 4: Monitoring (1 semana)
- [ ] OpenTelemetry integration
- [ ] Prometheus metrics
- [ ] Distributed tracing
- [ ] Alert setup
- [ ] Dashboards

### Sprint 5: DevOps (1 semana)
- [ ] Docker containers
- [ ] Kubernetes manifests
- [ ] CI/CD pipelines mejorada
- [ ] Infrastructure as Code
- [ ] Automated testing

---

## 📚 Recursos Recomendados

### Libros
- "Building Microservices" - Sam Newman
- "Release It!" - Michael Nygard
- "The Twelve-Factor App" - Adam Wiggins

### Tools
- **Logging**: Winston, Pino
- **Caching**: Redis, Memcached
- **Monitoring**: Prometheus, Grafana, DataDog
- **Tracing**: Jaeger, Zipkin, Google Cloud Trace
- **API Documentation**: Swagger/OpenAPI

---

## 🎯 Próximos Pasos Recomendados

1. **Comenzar con Logger** → Sustituir morgan por Winston
2. **Agregar Validación** → Implementar Zod en todos los endpoints
3. **Error Handling** → Crear clase AppError y middleware
4. **Testing** → Jest + Supertest para APIs
5. **Documentación** → OpenAPI spec

¿Por dónde empezamos?
