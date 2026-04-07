# ML Course Platform - Quick Reference Guide

## 🎯 System Overview

```
User Browser
    ↓
[Frontend - Next.js on Vercel/Netlify]
    ↓
[API Gateway/WAF]
    ↓
[Backend API - Express.js on Cloud Run/AppService]
    ↓
[PostgreSQL Database]  [S3/Blob Storage]  [ETL Pipeline]
```

---

## 📦 Components at a Glance

### Frontend (Next.js)
```bash
Location: ./frontend
Port: 3001
Stack: React + TypeScript + TailwindCSS
Deploy: Vercel (auto, free tier available)
```

**Key Routes:**
- `/` - Homepage
- `/courses` - Course listing
- `/courses/[id]` - Course detail
- `/admin` - Admin dashboard

### Backend (Express.js)
```bash
Location: ./backend
Port: 3000
Stack: Node.js + Express + Prisma + PostgreSQL
Deploy: AWS EC2/ECS, Azure App Service, Google Cloud Run
```

**API Endpoints:**
```
POST   /api/auth/oauth-callback      - User login
POST   /api/auth/refresh             - Token refresh
GET    /api/courses                  - List courses
GET    /api/courses/:id              - Course detail
POST   /api/courses                  - Create course (instructor)
POST   /api/uploads                  - Upload file
GET    /api/users/me                 - Current user
```

### Database (PostgreSQL)
```bash
Service: AWS RDS, Azure Database, Google Cloud SQL
Tables: users, roles, courses, chapters, figures, code_snippets, audit_logs
Encryption: At rest + encrypted backups
Backup: Daily, 30-day retention
```

### Storage (S3 / Blob)
```bash
Figures: s3://bucket/uploads/figures/
Code:    s3://bucket/uploads/code/
Assets:  s3://bucket/assets/

Encryption: AES-256
CDN: CloudFront / Azure CDN
Access: Private (presigned URLs)
```

### ETL Pipeline (Python)
```bash
Location: ./etl
Language: Python 3.11
Schedule: Daily 2 AM (GitHub Actions)
Input: GitHub (chapters/, code/)
Output: PostgreSQL + S3 + content.json

Process:
1. Extract (PyMuPDF, pdfminer, nbconvert)
2. Process (spaCy NLP, summarization, code highlighting)
3. Enrich (Deepl translation, keyword extraction)
4. Load (PostgreSQL, S3, CloudFront invalidation)
```

---

## 🔐 Security Layers

```
Layer 1: Network
├─ HTTPS/TLS 1.3+
├─ WAF (AWS/Azure)
└─ DDoS Protection

Layer 2: API
├─ Rate Limiting (100 req/15min)
├─ CORS Validation
├─ API Key Rotation
└─ JWT Tokens (15min expiry)

Layer 3: Authentication
├─ OAuth 2.0 (Google, GitHub, Microsoft)
├─ No password storage
├─ Email verification
└─ MFA support (optional)

Layer 4: Authorization
├─ Role-Based Access Control
├─ Fine-grained Permissions
├─ Resource-level Checks
└─ Admin approval workflows

Layer 5: Data Protection
├─ Encryption at Rest (AES-256)
├─ Encryption in Transit (TLS)
├─ Field-level Encryption
└─ Encrypted Backups

Layer 6: Monitoring
├─ Audit Logging (all actions)
├─ Anomaly Detection
├─ Real-time Alerts
└─ Incident Response
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (`npm test`)
- [ ] No security warnings (`npm audit`)
- [ ] Code reviewed & approved
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] SSL certificate valid
- [ ] Backups tested

### Deployment Command
```bash
# Staging
git push origin develop

# Production
git push origin main
# → Automatic deployment via GitHub Actions
```

### Post-Deployment
- [ ] Health check passing (`/health`)
- [ ] Database migrations applied
- [ ] API responding correctly
- [ ] Monitoring alerts active
- [ ] Logs being collected
- [ ] No critical errors in Sentry

---

## 📊 Key Metrics

| Metric | Target | Monitor |
|--------|--------|---------|
| API p99 latency | < 500ms | CloudWatch, DataDog |
| Error rate | < 0.1% | Sentry, Azure insights |
| Uptime | 99.9% | Health checks, PagerDuty |
| Database latency | < 100ms | RDS insights |
| ETL completion | < 30min | CloudWatch logs |

---

## 🛠️ Common Tasks

### Add a New Route
```typescript
// backend/src/routes/new.routes.ts
import { Router } from 'express';
import { authMiddleware, requireRole } from '../middleware/auth.middleware';

const router = Router();

router.get('/', async (req, res) => {
  // Handler
});

export default router;

// Add to backend/src/index.ts
import newRoutes from './routes/new.routes';
app.use('/api/new', newRoutes);
```

### Update Database Schema
```bash
cd backend

# Create migration
npx prisma migrate dev --name add_field_to_table

# Review changes in prisma/migrations/
# Deploy to production
npx prisma migrate deploy
```

### Run ETL Pipeline Manually
```bash
cd etl
python -m etl.pipeline \
  --course-id ml_course_001 \
  --source ./chapters \
  --verbose
```

### Clear Cache & Redeploy
```bash
# Clear S3 cache
aws s3 rm s3://bucket/content-feeds --recursive

# Invalidate CDN
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"

# Trigger redeployment
git commit --allow-empty -m "chore: cache invalidation"
git push origin main
```

---

## 🐛 Debugging

### Backend Logs
```bash
# Cloud provider logs
# AWS: CloudWatch
# Azure: Application Insights
# GCP: Cloud Logging

# Or tail locally
tail -f backend/logs/app.log
```

### Database Issues
```bash
# Connect to database
psql $DATABASE_URL

# Check migrations
npx prisma migrate status

# View query logs
SELECT * FROM pg_stat_statements LIMIT 10;
```

### ETL Pipeline Issues
```bash
# Run with verbose logging
python -m etl.pipeline \
  --course-id ml_course_001 \
  --source ./chapters \
  --verbose

# Check S3 uploads
aws s3 ls s3://bucket/uploads/ --recursive

# View PostgreSQL inserts
SELECT * FROM chapters WHERE created_at > now() - interval '1 hour';
```

---

## 📚 File Locations

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment variables |
| `prisma/schema.prisma` | Database schema definition |
| `backend/src/routes/` | API route handlers |
| `backend/src/middleware/` | Express middlewares |
| `etl/src/pipeline.py` | ETL orchestrator |
| `.github/workflows/` | CI/CD automation |
| `docs/` | Documentation |

---

## 🔄 CI/CD Pipeline

```
git push origin feature/branch
        ↓
GitHub Actions Triggered
        ├─ Lint (ESLint)
        ├─ Test (Jest, Pytest)
        ├─ Security Scan (Snyk, CodeQL)
        ├─ Build (Next.js, Node.js)
        └─ Report Coverage
            ↓
    [Wait for Review]
        ↓
git push origin main (merge PR)
        ├─ Run full test suite
        ├─ Build Docker images
        ├─ Push to registry
        └─ Deploy to staging
            ↓
    [Manual approval]
        ↓
    Deploy to production
        ├─ Database migrations
        ├─ API deployment
        ├─ Frontend deployment
        └─ Health checks
```

---

## 💰 Cost Optimization

| Service | Est. Cost | Notes |
|---------|-----------|-------|
| PostgreSQL RDS | $50-200/mo | db.t3.micro to higher |
| S3 Storage | $25-100/mo | 1TB + 10TB bandwidth |
| Backend | $50-500/mo | Pay-as-you-go or reserved |
| Frontend | $0-50/mo | Vercel free + overage |
| ETL | $20-200/mo | Scheduled batch processing |
| **Total** | **$200-1050/mo** | Production baseline |

**Optimization Tips:**
- Use reserved instances for predictable workloads
- S3 Glacier for cold data
- CloudFront for CDN caching
- API Gateway caching for frequent requests

---

## 🚨 Incident Response

### If API is Down
1. Check health endpoint: `GET /health`
2. Review CloudWatch/Azure Monitor logs
3. Check database connectivity
4. Rollback if recent deployment
5. Notify users if > 5min downtime

### If Database is Slow
1. Check RDS metrics (CPU, connections)
2. Review slow query logs
3. Add indexes if needed
4. Scale up instance if load high
5. Review recent migrations

### If ETL Pipeline Fails
1. Check GitHub Actions logs
2. Verify S3 access
3. Check database space
4. Validate source files
5. Review error details in Sentry

### If Security Alert
1. Isolate affected resources
2. Review audit logs
3. Rotate compromised credentials
4. Check for data exfiltration
5. Notify security team

---

## 📞 Quick Contacts

- **Slack**: #ml-course-platform
- **On-call**: PagerDuty (engineering-oncall)
- **Security**: security@company.com
- **Escalation**: @engineering-lead

---

## ✅ Pre-Production Checklist

- [ ] Load testing (locust, k6)
- [ ] Penetration testing scheduled
- [ ] Disaster recovery plan documented
- [ ] All team trained on runbooks
- [ ] On-call rotation set up
- [ ] Escalation procedures clear
- [ ] Monitoring dashboards created
- [ ] Alert thresholds validated
- [ ] Backup tested & restored
- [ ] RTO/RPO targets met

---

**Last Updated:** March 27, 2026  
**Maintained by:** Engineering Team  
**Next Review:** June 27, 2026
