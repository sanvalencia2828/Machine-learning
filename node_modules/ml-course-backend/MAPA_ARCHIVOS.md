# 📖 MAPA DE ARCHIVOS - Backend Profesional

**Tu Backend** | **Estructura Completa** | **Propósito de cada archivo**

---

## 📋 Índice Rápido

- [🚀 COMIENZA AQUÍ](#-comienza-aquí)
- [📁 Estructura de Carpetas](#-estructura-de-carpetas)
- [🔴 CORE: Códigos Principales](#-core-códigos-principales)
- [🟡 MIDDLEWARE: Funcionalidad Cross-Cutting](#-middleware-funcionalidad-cross-cutting)
- [🟢 UTILITIES: Herramientas Auxiliares](#-utilities-herramientas-auxiliares)
- [🔵 CONFIGURATION: Archivos de Config](#-configuration-archivos-de-config)
- [🟣 DOCUMENTATION: Guías y Docs](#-documentation-guías-y-docs)
- [🏗️ Architecture Decision Records](#-architecture-decision-records)

---

## 🚀 COMIENZA AQUÍ

### 1️⃣ Para ejecutar el backend
→ [QUICK_START.md](#) - **5 minutos para empezar**
```bash
cd backend
npm install
cp .env.example .env.local
npm run dev
```

### 2️⃣ Para entender la arquitectura
→ [RESUMEN_IMPLEMENTACION.md](#) - **Qué se hizo y por qué**

### 3️⃣ Para usar las APIs
→ [README.md](#) - **Documentación de endpoints**

### 4️⃣ Para el próximo paso
→ [FASE_2_PROXIMO.md](#) - **Database optimization strategy**

---

## 📁 ESTRUCTURA DE CARPETAS

```
backend/
├── src/                          ← 🔥 TODO EL CÓDIGO FUENTE
│   ├── index.ts                 ← 🚀 PUNTO DE ENTRADA (Express server)
│   ├── lib/                     ← 📚 Librerías compartidas
│   ├── middleware/              ← ⚙️ Middleware (5 files)
│   ├── types/                   ← 🏷️ Type definitions
│   ├── schemas/                 ← ✔️ Zod validation schemas
│   ├── services/                ← 🛠️ Business logic services
│   ├── routes/                  ← 🛣️ Route definitions
│   └── utils/                   ← 🔧 Utility functions
│
├── logs/                        ← 📂 Logs generados (ignored by git)
│
├── node_modules/               ← 📦 Dependencies (ignored by git)
│
├── package.json                ← ⚙️ Dependencies & scripts
├── tsconfig.json              ← 🔷 TypeScript config
├── .env.example               ← 🔐 Environment template
├── .env.local                 ← 🔐 Local values (NO COMMIT)
├── .gitignore                 ← 🚫 Git ignore rules
├── .eslintrc.json            ← 📏 Linting rules
├── .prettierrc                ← 🎨 Code formatting
│
├── README.md                  ← 📖 API Documentation
├── QUICK_START.md             ← ⚡ Quick start guide
├── RESUMEN_IMPLEMENTACION.md  ← 📊 Implementation summary
└── FASE_2_PROXIMO.md         ← 🔮 Next phase preview
```

---

## 🔴 CORE: CÓDIGOS PRINCIPALES

### `src/index.ts` - Express Server Root
**Tamaño**: ~150 líneas | **Criticidad**: 🔴 CRÍTICO

**Qué hace:**
```
✅ Inicializa Express app
✅ Configura TODAS las middlewares
✅ Integra TODAS las rutas
✅ Maneja 404s y errores globales
✅ Maneja signals (SIGTERM)
✅ Inicia el servidor
```

**¿Cuándo lo necesitas?**
- Para agregar nuevas middlewares
- Para agregar nuevas rutas
- Para cambiar orden de middlewares (CUIDADO!)
- Para cambiar puerto o configuración

**Flujo:**
```
Client Request → Helmet → CORS → Compression → Parsing
  ↓
Correlation ID → Logging → RateLimiting → Routes
  ↓
(Handler succeeds) → ResponseJSON → Logging Middleware → Client
       ↓
(Handler throws Error) → ErrorHandler → JSON Response → Client
```

---

## 🟡 MIDDLEWARE: FUNCIONALIDAD CROSS-CUTTING

### `src/middleware/correlation-id.middleware.ts`
**Tamaño**: 23 líneas | **Criticidad**: 🟡 IMPORTANTE

**¿Qué hace?**
```typescript
1. Genera UUID único para cada request
2. Lo asigna como X-Correlation-ID header
3. Lo inyecta en Winston logger
4. Permite rastrear requests en logs
```

**¿Cuándo lo necesitas?**
- Cuando necesitas debuggear un request específico
- Para trazabilidad en microservicios
- Para connected transactions

**Ejemplo uso en logs:**
```
[GET /api/users] correlationId: abc123 | 45ms ✅
grep "abc123" logs/combined-*.log  ← Encuentra TODOS los logs de ese request
```

---

### `src/middleware/logging.middleware.ts`
**Tamaño**: 43 líneas | **Criticidad**: 🟡 IMPORTANTE

**¿Qué hace?**
```typescript
1. Captura cada response
2. Registra: statusCode, contentLength, duration
3. Elige nivel (info/warn/error según status)
4. Logea userId, userAgent, IP
5. Envía a Winston logger
```

**¿Cuándo lo necesitas?**
- Para monitoria de API
- Para detectar problemas de performance
- Para auditoría de accesos

**Qué ves en logs:**
```
[2026-04-07 10:30:45] POST /api/auth/login - 200 - 45ms
[2026-04-07 10:30:46] GET /api/courses - 400 - 12ms (WARN)
[2026-04-07 10:30:47] DELETE /api/user/123 - 500 - 134ms (ERROR)
```

---

### `src/middleware/error-handler.middleware.ts`
**Tamaño**: 86 líneas | **Criticidad**: 🔴 CRÍTICO

**¿Qué hace?**
```typescript
1. Catch TODOS los errores (try/catch a nivel superior)
2. Identifica tipo de error (AppError vs Prisma vs unknown)
3. Sanitiza mensajes (no leak info en PROD)
4. Logea con stack trace en DEV
5. Retorna JSON standardizado
6. Setea HTTP status correcto
```

**¿Cuándo lo necesitas?**
- SIEMPRE - Es el último line of defense contra crashes
- Para cambiar formato de error responses
- Para agregar custom error handling

**Estructura de Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR | AUTH_ERROR | NOT_FOUND | etc",
    "message": "User-friendly message",
    "details": [{ "field": "email", "message": "..." }],
    "correlationId": "abc123..."
  }
}
```

---

### `src/middleware/validate.middleware.ts`
**Tamaño**: 79 líneas | **Criticidad**: 🟡 IMPORTANTE

**¿Qué hace?**
```typescript
1. Valida request body contra Zod schema
2. Valida query params contra schema
3. Valida route params contra schema
4. Retorna ValidationError si falla
5. Deja pasar si OK
```

**¿Cuándo lo necesitas?**
- En TODAS las rutas que aceptan datos
- Para garantizar tipos correctos
- Para validación de negocio

**Ejemplo uso en ruta:**
```typescript
router.post(
  '/login',
  validate(loginSchema),  ← ✅ Validación automática
  asyncHandler(loginHandler)
);
```

---

### `src/middleware/rate-limit.middleware.ts`
**Tamaño**: 64 líneas | **Criticidad**: 🟠 RECOMENDADO

**¿Qué hace?**
```typescript
1. Crea 5 limiters diferentes
2. General: 100 req/15 min
3. Auth: 5 req/15 min
4. API: 30 req/min
5. Upload: 50 req/24h
6. Strict: 10 req/1h
7. Admin: Sin límite
```

**¿Cuándo lo necesitas?**
- Para proteger contra DDoS
- Para evitar brute force en login
- Para limitar rate de uploads

**Ejemplo:**
```typescript
// En src/index.ts
app.post('/api/auth/login', limiters.auth, handler);
app.post('/api/upload', limiters.upload, handler);
```

---

## 🟢 UTILITIES: HERRAMIENTAS AUXILIARES

### `src/lib/logger.ts` - Winston Logger
**Tamaño**: 60 líneas | **Criticidad**: 🟡 IMPORTANTE

**¿Qué hace?**
```typescript
1. Configura Winston logger
2. 3 transports (console, combined file, error file)
3. Daily rotation (nuevo archivo cada día)
4. JSON format para parsing
5. Colorized console para desarrollo
6. Exception handlers integrados
```

**¿Cuándo lo necesitas?**
- Para loguear desde servicios/handlers
- Para debugging
- Para auditoría

**Ejemplo uso:**
```typescript
import logger from '@/lib/logger';

logger.info('User login successful', { userId: 123, ip: req.ip });
logger.warn('Invalid login attempt', { email, reason: 'wrong password' });
logger.error('Database connection failed', { error: err.message });
```

**Archivos generados:**
```
logs/
├── combined-2026-04-07.log  (TODOS)
├── combined-2026-04-08.log  (Ayer)
├── error-2026-04-07.log     (Solo ERRORS)
└── exceptions-2026-04-07.log (Crashes)
```

---

### `src/lib/prisma.ts` - Prisma ORM
**Tamaño**: 25 líneas | **Criticidad**: 🔴 CRÍTICO

**¿Qué hace?**
```typescript
1. Singleton pattern para Prisma client
2. Query logging en DEV
3. Error event handlers
4. Global persistence prevention
5. Dev-only console setup
```

**¿Cuándo lo necesitas?**
- Para queryear la database
- Para debugging queries
- Para error handling en queries

**Ejemplo uso:**
```typescript
import { prisma } from '@/lib/prisma';

// Query automáticamente logueada en DEV
const user = await prisma.user.findUnique({ 
  where: { id: '123' } 
});

// Con error handling automático del middleware
```

---

### `src/utils/async-handler.ts`
**Tamaño**: 13 líneas | **Criticidad**: 🔴 CRÍTICO

**¿Qué hace?**
```typescript
export const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};
```

**¿Cuándo lo necesitas?**
- En TODAS las rutas async
- Para propagar errores al errorHandler

**Ejemplo uso:**
```typescript
router.post('/course', 
  validate(createCourseSchema),
  asyncHandler(async (req, res) => {
    const course = await prisma.course.create({ ... });
    res.json(course);
    // ✅ Si hay error, catch automático → errorHandler
  })
);
```

---

## 🟠 TYPES & SCHEMAS

### `src/types/errors.ts` - Error Classes
**Tamaño**: 120 líneas | **Criticidad**: 🔴 CRÍTICO

**Qué contiene:**
```typescript
✅ ResponseCode enum (11 códigos)
✅ AppError base class
✅ 8 Error subclasses:
   - ValidationError
   - AuthenticationError  
   - AuthorizationError
   - NotFoundError
   - ConflictError
   - BadRequestError
   - DatabaseError
   - RateLimitError
```

**¿Cuándo lo necesitas?**
- Cuando necesitas throw un error tipado
- Para respuestas standardizadas
- Para debugging

**Ejemplo uso:**
```typescript
import { ValidationError, NotFoundError } from '@/types/errors';

if (!user) {
  throw new NotFoundError('User', userId);
}

if (email.includes('@') === false) {
  throw new ValidationError('Invalid email', { email });
}
```

---

### `src/schemas/auth.schema.ts` - Auth Validation
**Tamaño**: 47 líneas | **Criticidad**: 🟡 IMPORTANTE

**Schemas incluidos:**
```typescript
✅ signUpSchema
   - email (valid email)
   - password (12+ chars, upper, lower, num, special)
   - passwordConfirm (must match)
   - fullName

✅ loginSchema
   - email
   - password

✅ refreshTokenSchema
   - refreshToken

✅ forgotPasswordSchema
   - email

✅ resetPasswordSchema
   - token
   - password
   - passwordConfirm
```

**¿Cuándo lo necesitas?**
- Para validar solicitudes de auth
- Para cambiar reglas de validación
- Para agregar campos nuevos

**Ejemplo uso:**
```typescript
router.post('/signup', validate(signUpSchema), asyncHandler(handler));
```

---

### `src/schemas/course.schema.ts` - Course Validation
**Tamaño**: 85 líneas | **Criticidad**: 🟡 IMPORTANTE

**Schemas incluidos:**
```typescript
✅ createCourseSchema
✅ updateCourseSchema
✅ listCoursesSchema (pagination, sorting)
✅ chapterSchema
✅ contentSchema
✅ enrollmentSchema
✅ reviewSchema
```

---

## 🔵 CONFIGURATION: ARCHIVOS DE CONFIG

### `package.json`
**Tamaño**: ~80 líneas | **Criticidad**: 🔴 CRÍTICO

**Contiene:**
```
✅ 30+ production dependencies (express, prisma, winston, zod, etc)
✅ 15+ dev dependencies (typescript, eslint, jest, etc)
✅ 6+ scripts (dev, build, start, lint, test)
✅ TypeScript config
✅ ESLint config referencia
```

**Scripts:**
```bash
npm run dev           # Desarrollo con hot reload
npm run build        # Compilar
npm run start        # Run compiled
npm run lint         # Check code style
npm run lint:fix     # Fix code style
npm run test         # Test suite
npm run test:coverage # Coverage report
```

---

### `tsconfig.json`
**Tamaño**: ~35 líneas | **Criticidad**: 🟠 RECOMENDADO

**Features:**
```
✅ Strict mode habilitado
✅ Resolución de paths (@/)
✅ Target ES2020
✅ Source maps en dev
✅ Declaration files generados
✅ Module resolution: node
```

---

### `.env.example` - Template Variables
**Tamaño**: ~50 líneas | **Criticidad**: 🔴 CRÍTICO

**Contiene 40+ variables:**
```
NODE_ENV               - development|production|test
PORT                  - 3000
DATABASE_URL          - PostgreSQL connection
JWT_SECRET            - Token secret (min 32 chars)
JWT_REFRESH_SECRET    - Refresh token secret
JWT_EXPIRATION        - Token expiration time
OAUTH_GOOGLE_*        - Google OAuth credentials
OAUTH_GITHUB_*        - GitHub OAuth credentials
AWS_*                 - AWS S3 credentials
REDIS_*               - Redis connection
SMTP_*                - Email service
API_*                 - External APIs
FEATURE_FLAGS_*       - Feature toggles
```

**¿Qué hacer?**
1. `cp .env.example .env.local`
2. Editar `.env.local` con tus valores
3. NUNCA commitear `.env.local`
4. NUNCA pushear secrets

---

### `.gitignore` - Git Ignore Rules
**Tamaño**: ~40 líneas | **Criticidad**: 🔴 CRÍTICO

**Protege:**
```
node_modules/
.env.local
.env.*.local
dist/
build/
logs/
coverage/
.vscode/
.idea/
*.log
.DS_Store
```

---

### `.eslintrc.json`, `.prettierrc`
**Criticidad**: 🟠 RECOMENDADO

**ESLint:**
```json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "env": { "node": true, "es2020": true }
}
```

**Prettier:**
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

## 🟣 DOCUMENTATION: GUÍAS Y DOCS

### `README.md` - API Documentation
**Tamaño**: ~130 líneas | **Criticidad**: 🟡 IMPORTANTE

**Contiene:**
```
✅ Features overview
✅ Quick start guide
✅ Available scripts
✅ Project structure
✅ API endpoints (todos)
✅ Authentication flow
✅ Logging explanation
✅ Validation explanation
✅ Rate limiting explanation
✅ Testing guide
✅ Database connection
✅ Deployment guide
✅ Monitoring guide
```

---

### `QUICK_START.md` - This Quick Start Guide
**Tamaño**: ~200 líneas | **Criticidad**: 🟡 IMPORTANTE

**Contiene:**
```
✅ 5-minute quick start
✅ npm commands
✅ Verification steps
✅ Debugging tips
✅ Error troubleshooting
✅ Feature overview
✅ Next steps
```

---

### `RESUMEN_IMPLEMENTACION.md` - Implementation Summary
**Tamaño**: ~250 líneas | **Criticidad**: 🟡 IMPORTANTE

**Contiene:**
```
✅ What was completed
✅ Architecture diagram (texto)
✅ Improvements summary
✅ Security hardening
✅ Performance impact
✅ Next phases preview
✅ ROI analysis
```

---

### `FASE_2_PROXIMO.md` - Phase 2 Preview
**Tamaño**: ~200 líneas | **Criticidad**: 🟠 RECOMENDADO

**Preview de próxima fase:**
```
✅ Database optimization strategy
✅ Connection pooling setup
✅ Index creation queries
✅ Query optimization examples
✅ Transaction patterns
✅ Performance measurement
✅ Timeline: 1 week
```

---

## 🏗️ ARCHITECTURE DECISION RECORDS

### Outside `backend/` folder (at project root):

1. **`ARCHITECTURE_PROFESSIONAL_GUIDE.md`** (10+ pages)
   - 7 Pillars of professional architecture
   - Complete code examples for each pillar
   - Security best practices
   - Database optimization patterns
   - Caching strategies
   - API versioning approaches
   - Monitoring/observability setup

2. **`IMPLEMENTATION_ROADMAP.md`** (15+ pages)
   - 5 Phases with copy-paste code
   - Verification checklists for each phase
   - Time estimates per phase
   - Dependencies to install
   - Testing strategies

3. **`FRONTEND_DATABASE_ARCHITECTURE.md`**
   - Next.js folder structure
   - API client pattern
   - Custom hooks organization
   - Zustand store setup
   - Complete Prisma schema optimized for the domain

4. **`RESUMEN_EJECUTIVO_Y_PLAN.md`**
   - Executive summary
   - 4-week roadmap with milestones
   - Before/after metrics
   - Team responsibilities
   - Risk mitigation

5. **`CHECKLIST_28_DIAS.md`**
   - Day-by-day detailed tasks
   - Specific success criteria per day
   - Time estimates per task
   - Tips for staying on track
   - Weekly reviews

---

## 📍 MAPA DE NAVEGACIÓN

### ¿Necesitas ayuda con...?

**Starting up?**
→ `QUICK_START.md` → `npm run dev`

**Understanding architecture?**
→ `RESUMEN_IMPLEMENTACION.md` → `ARCHITECTURE_PROFESSIONAL_GUIDE.md`

**Adding a new route?**
→ `src/schemas/*.ts` (crear schema)
→ `src/routes/*.ts` (crear ruta)
→ `src/services/*.ts` (crear servicio)

**Debugging an error?**
→ `tail -f logs/combined-*.log`
→ Search for correlationId
→ Check `src/types/errors.ts`

**Understanding a middleware?**
→ `src/middleware/*.ts`
→ Flow diagram in: `RESUMEN_IMPLEMENTACION.md`

**Deploying?**
→ `FASE_2_PROXIMO.md` → `IMPLEMENTACIÓN_ROADMAP.md`

**I broke something?**
→ `npm run lint:fix`
→ `npm run build`

---

## 🎯 QUICK REFERENCE COMMANDS

```bash
# 📂 Navigation
cd backend
ls src/                      # Ver source code
tail -f logs/combined-*.log # Ver logs en vivo

# 🚀 Execution
npm run dev                 # Desarrollar
npm run build              # Compilar
npm run start              # Correr compilado

# 🧹 Cleanup
npm run lint:fix           # Arreglar codigo
rm -rf logs/*             # Limpiar logs

# 🔍 Debugging
grep "ERROR" logs/error-*.log
grep "correlationId-abc123" logs/*
curl -i http://localhost:3000/health

# 📋 Verification
npm run build && echo "✅ OK"
npm run lint && echo "✅ OK"
```

---

## 📊 FILES BY CRITICALITY

### 🔴 CRITICAL (System won't work without)
- `src/index.ts`
- `src/middleware/error-handler.middleware.ts`
- `src/utils/async-handler.ts`
- `src/lib/logger.ts`
- `src/lib/prisma.ts`
- `src/types/errors.ts`
- `package.json`
- `.env.example`

### 🟡 IMPORTANT (Core functionality)
- `src/middleware/correlation-id.middleware.ts`
- `src/middleware/logging.middleware.ts`
- `src/middleware/validate.middleware.ts`
- `src/schemas/*.ts`
- `src/services/health.service.ts`
- `README.md`

### 🟠 RECOMMENDED (Quality/convenience)
- `src/middleware/rate-limit.middleware.ts`
- `.eslintrc.json`
- `.prettierrc`
- `tsconfig.json`
- `QUICK_START.md`

---

## 🎉 SUMMARY

**Total Files**: 20+  
**Total Lines**: 2000+  
**Architecture**: Professional ⭐⭐⭐⭐⭐  
**Production Ready**: ✅ YES  
**Time to Understand**: ~1 hour  
**Time to Deploy**: ~5 minutes  

**Everything is documented, typed, and ready.**

---

*Map Version: 1.0*  
*Last Updated: April 7, 2026*  
*Status: Complete ✅*
