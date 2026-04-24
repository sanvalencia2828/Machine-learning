# ML Course Platform - Backend API

Professional backend API for ML Course Platform with logging, error handling, validation, and monitoring.

## ✨ Features

- ✅ **Structured Logging** - Winston logger with daily rotation
- ✅ **Error Handling** - Standardized error responses
- ✅ **Validation** - Zod schemas for type-safe validation
- ✅ **Rate Limiting** - Per-endpoint rate limiting
- ✅ **Health Checks** - Liveness and readiness probes
- ✅ **Correlation IDs** - Request tracking across logs
- ✅ **Security** - Helmet, CORS, compression
- ✅ **Database** - Prisma ORM with PostgreSQL
- ✅ **Authentication** - OAuth 2.0 and JWT
- ✅ **Authorization** - RBAC with permissions

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local with your values
nano .env.local

# Setup database
npm run db:migrate

# Start development server
npm run dev
```

Server runs at: `http://localhost:3000`

## 📁 Project Structure

```
src/
├── lib/
│   ├── logger.ts          # Winston logger configuration
│   └── prisma.ts          # Prisma ORM setup
├── middleware/
│   ├── correlation-id.middleware.ts  # Request tracking
│   ├── logging.middleware.ts         # Response logging
│   ├── error-handler.middleware.ts   # Error handling
│   ├── validate.middleware.ts        # Request validation
│   └── rate-limit.middleware.ts      # Rate limiting
├── types/
│   └── errors.ts          # Error types and classes
├── schemas/
│   ├── auth.schema.ts     # Authentication validation
│   └── course.schema.ts   # Course validation
├── services/
│   └── health.service.ts  # Health check service
├── routes/
│   └── health.routes.ts   # Health check endpoints
├── utils/
│   └── async-handler.ts   # Async route wrapper
└── index.ts               # Server entry point
```

## 🛠️ Available Scripts

```bash
# Development
npm run dev              # Start with auto-reload

# Production
npm run build            # Build TypeScript
npm start                # Run production build

# Database
npm run db:migrate       # Run migrations
npm run db:generate      # Generate Prisma types
npm run db:studio        # Open Prisma Studio

# Code Quality
npm run lint             # Run ESLint
npm run format           # Format with Prettier
npm run test             # Run tests
npm run test:coverage    # Coverage report

# Security
npm run security-check   # Check vulnerabilities
```

## 📋 API Endpoints

### Health Checks
```
GET  /health          # Simple health check
GET  /health/ready    # Readiness probe
GET  /health/live     # Liveness probe
GET  /status          # Detailed status
```

### Test Endpoint
```
GET  /api/test        # Test API connection
```

## 🔐 Authentication & Security

### Environment Variables Required
```
JWT_SECRET              # Secret for signing JWTs
JWT_REFRESH_SECRET      # Secret for refresh tokens
GOOGLE_CLIENT_ID        # Google OAuth credentials
GOOGLE_CLIENT_SECRET    # Google OAuth credentials
DATABASE_URL            # PostgreSQL connection string
```

### Security Features
- Helmet.js headers
- CORS protection
- Rate limiting
- Input validation
- Error sanitization in production

## 📊 Logging

### Log Levels
- `debug` - Development only
- `info` - General information
- `warn` - Warnings
- `error` - Errors

### Log Files
- `logs/combined-YYYY-MM-DD.log` - All logs
- `logs/error-YYYY-MM-DD.log` - Errors only
- `logs/exceptions-YYYY-MM-DD.log` - Uncaught exceptions

### Request Correlation
Every request has an `X-Correlation-ID` header for tracking:
```typescript
// Response headers
X-Correlation-ID: req_1234567890_abc123def
```

## ✔️ Request Validation

All endpoints use Zod schemas for validation:

```typescript
// Authentication
POST /api/auth/login      { email, password }
POST /api/auth/register   { email, name, password, passwordConfirm }

// Courses
GET  /api/courses         { page?, limit?, status?, search? }
POST /api/courses         { titleEs, titleEn, description, price }
GET  /api/courses/{id}    
PUT  /api/courses/{id}    { partial course data }
```

## 🚦 Rate Limiting

- General API: 100 requests per 15 minutes
- Auth endpoints: 5 attempts per 15 minutes
- Upload: 50 per 24 hours
- Strict endpoints: 10 per hour

Admin users are exempt from rate limiting.

## 📈 Monitoring

### Available Metrics
- Request count and latency
- Error rates
- Database connection health
- Uptime status

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2026-04-07T10:30:00Z",
  "uptime": 3600.5,
  "database": {
    "status": "up",
    "latency": 5
  },
  "checks": [
    {
      "name": "database",
      "status": "pass",
      "latency": 5
    }
  ]
}
```

## 🧪 Testing

```bash
# Run all tests
npm run test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## 🔄 Database Migrations

```bash
# Create new migration
npm run db:migrate -- --name add_new_table

# View migration history
npm run db:studio
```

## 🚢 Deployment

### Docker

```bash
docker build -t ml-backend .
docker run -p 3000:3000 ml-backend
```

### Environment Variables (Production)
- Set `NODE_ENV=production`
- Enable HTTPS
- Use strong secrets
- Configure database URL
- Setup monitoring

## 📚 Architecture

See [ARCHITECTURE.md](../ARCHITECTURE_PROFESSIONAL_GUIDE.md) for detailed architecture documentation.

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests: `npm run test`
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/your-feature`

## 📝 License

MIT

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Status**: Production Ready ✅  
**Last Updated**: April 2026  
**Version**: 1.0.0
