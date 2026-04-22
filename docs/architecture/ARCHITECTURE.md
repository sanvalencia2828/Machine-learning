# ML Course Platform - Architecture Overview

## Project Structure

```
ml-course-platform/
├── frontend/                 # Next.js UI (Vercel/Netlify)
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/                  # Node.js/Express API
│   ├── src/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── middleware/
│   │   ├── models/
│   │   └── config/
│   └── tests/
├── cms/                      # Strapi/Sanity configuration
│   └── types/
├── etl/                      # Python document processing pipeline
│   ├── extractors/           # PyMuPDF, pdfminer
│   ├── processors/           # NLP, summarization
│   ├── loaders/              # S3, PostgreSQL
│   └── orchestration/        # Airflow/Prefect configs
├── database/                 # Database migrations & schemas
│   ├── migrations/
│   └── seeds/
├── infrastructure/           # IaC (Terraform/Bicep)
│   ├── terraform/
│   └── docker/
├── github-actions/           # CI/CD workflows
│   └── workflows/
└── docs/                     # Documentation
    ├── API.md
    ├── SECURITY.md
    ├── DEPLOYMENT.md
    └── CONTRIBUTING.md
```

---

## 1. Backend Architecture

### Stack
- **Framework**: Node.js + Express (or Next.js API routes)
- **Authentication**: OAuth 2.0 (Google, GitHub, Microsoft)
- **Authorization**: Role-based access control (RBAC)
- **Database ORM**: Prisma or TypeORM
- **Validation**: Zod or Joi
- **API Documentation**: OpenAPI/Swagger

### Authentication Flow
```
User → OAuth Provider → Backend → JWT Token → Frontend
                          ↓
                      PostgreSQL (user_profiles, roles)
```

### Key Endpoints
```
/api/auth/login              - OAuth callback
/api/auth/logout             - Session cleanup
/api/auth/refresh            - JWT refresh
/api/users/{id}              - User management
/api/courses                 - List/create courses
/api/courses/{id}            - Course details
/api/courses/{id}/chapters   - Chapter management
/api/content/{id}            - Content delivery
/api/uploads                 - File upload with validation
```

---

## 2. Content Management System (CMS)

### Option: Strapi (Recommended)
- Self-hosted or SaaS
- Built-in role/permission system
- Multi-language support via plugins
- Custom content types for courses, chapters, figures

### Core Content Types
```typescript
// Course
{
  id: string
  title: { es: string, en: string }
  description: { es: string, en: string }
  price: { currency: string, amount: number }
  collaborationStatus: enum
  translations: { es: string, en: string }
  lastUpdated: datetime
  chapters: Chapter[]
}

// Chapter
{
  id: string
  courseId: string
  title: { es: string, en: string }
  summary: { es: string, en: string }
  keywords: string[]
  figures: Figure[]
  codeSnippets: CodeSnippet[]
}

// Figure
{
  id: string
  chapterId: string
  s3Key: string
  caption: { es: string, en: string }
  alt: { es: string, en: string }
}

// CodeSnippet
{
  id: string
  chapterId: string
  language: string
  s3Key: string  // Raw code file
  description: { es: string, en: string }
}
```

### Webhook Triggers
- On content publish → Trigger ETL pipeline
- On file upload → Generate S3 presigned URLs
- On translation update → Regenerate content.json

---

## 3. Database Schema (PostgreSQL)

### Core Tables
```sql
-- Users & Auth
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  oauth_provider VARCHAR,
  oauth_id VARCHAR,
  name VARCHAR,
  created_at TIMESTAMP
);

CREATE TABLE roles (
  id UUID PRIMARY KEY,
  name VARCHAR UNIQUE, -- admin, instructor, student, viewer
  permissions JSONB
);

CREATE TABLE user_roles (
  user_id UUID REFERENCES users(id),
  role_id UUID REFERENCES roles(id),
  course_id UUID (optional, for course-level roles),
  PRIMARY KEY (user_id, role_id)
);

-- Content
CREATE TABLE courses (
  id UUID PRIMARY KEY,
  title_es VARCHAR,
  title_en VARCHAR,
  created_by UUID REFERENCES users(id),
  metadata JSONB, -- price, collaboration_status, etc.
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE chapters (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(id),
  title_es VARCHAR,
  title_en VARCHAR,
  order INT,
  content_json JSONB, -- Populated by ETL
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE figures (
  id UUID PRIMARY KEY,
  chapter_id UUID REFERENCES chapters(id),
  s3_key VARCHAR,
  caption_es TEXT,
  caption_en TEXT
);

CREATE TABLE code_snippets (
  id UUID PRIMARY KEY,
  chapter_id UUID REFERENCES chapters(id),
  language VARCHAR,
  s3_key VARCHAR,
  description_es TEXT,
  description_en TEXT
);

-- Audit & Access Control
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR,
  resource_type VARCHAR,
  resource_id UUID,
  timestamp TIMESTAMP,
  ip_address INET,
  metadata JSONB
);
```

---

## 4. Document Processing ETL Pipeline (Python)

### Architecture
```
GitHub/S3 (PDFs, Notebooks)
    ↓
ETL Orchestrator (Airflow/Prefect)
    ↓
┌─────────────────────────────┐
│ Extraction Layer            │
│ - PyMuPDF (PDF metadata)    │
│ - pdfminer (text extraction)│
│ - nbconvert (notebooks)     │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│ Processing Layer            │
│ - NLP (spaCy, transformers) │
│ - Summarization             │
│ - Code snippet extraction   │
│ - Figure detection          │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│ Enrichment Layer            │
│ - Translation (DeepL API)   │
│ - Keyword extraction        │
│ - Cross-reference links     │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│ Loading Layer               │
│ - PostgreSQL (metadata)     │
│ - S3 (raw assets)           │
│ - content.json (feed data)  │
└─────────────────────────────┘
```

### Key Processors
```python
# extractors/pdf_extractor.py
- extract_text(pdf_path) → str
- extract_metadata(pdf_path) → dict
- extract_figures(pdf_path) → List[Image]

# processors/nlp_processor.py
- summarize(text, lang) → str
- extract_keywords(text) → List[str]
- detect_language(text) → str

# processors/code_processor.py
- extract_code_blocks(text) → List[CodeSnippet]
- syntax_highlight(code, language) → str

# loaders/database_loader.py
- write_chapter(chapter_data) → UUID
- write_figures(figures) → List[UUID]
- write_code_snippets(snippets) → List[UUID]

# orchestration/pipeline.py
- run_course_etl(course_id, source_path)
- validate_output()
- generate_content_json()
```

### Output: content.json
```json
{
  "course": {
    "id": "ml_course_001",
    "title": {"es": "...", "en": "..."},
    "chapters": [
      {
        "id": "ch01",
        "title": {"es": "...", "en": "..."},
        "summary": {"es": "...", "en": "..."},
        "keywords": ["bayesiano", "prior"],
        "figures": [
          {
            "id": "fig1",
            "s3_url": "https://bucket.s3.amazonaws.com/...",
            "caption": {"es": "...", "en": "..."}
          }
        ],
        "code_snippets": [
          {
            "id": "code1",
            "language": "python",
            "s3_url": "https://bucket.s3.amazonaws.com/...",
            "description": {"es": "...", "en": "..."}
          }
        ]
      }
    ]
  }
}
```

---

## 5. GitHub Integration

### Repository Structure per Product
```
github.com/org/ml_course_001/
├── README.md
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint, test, build notebooks
│       ├── etl.yml             # Trigger ETL on commit
│       └── security-scan.yml   # SAST, dependency check
├── chapters/
│   ├── ch01/
│   │   ├── ch01.pdf
│   │   ├── notebook.ipynb
│   │   └── figures/
│   └── ch02/
├── code/
│   ├── requirements.txt
│   ├── setup.py
│   └── examples/
├── data/
│   └── .gitattributes         # Git LFS for large files
└── translations/
    ├── es.yml
    └── en.yml
```

### GitHub Actions Workflows

#### 1. CI Pipeline (ci.yml)
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest chapters/ --cov
      - run: jupyter nbconvert --to notebook --execute chapters/*/notebook.ipynb
      - uses: codecov/codecov-action@v3
```

#### 2. ETL Trigger (etl.yml)
```yaml
on:
  push:
    paths:
      - 'chapters/**'
      - 'code/**'
  workflow_dispatch:
jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          lfs: true
      - run: python -m etl.orchestration.pipeline --course-id ${{ secrets.COURSE_ID }}
      - uses: actions/upload-artifact@v3
        with:
          name: content.json
          path: output/content.json
```

---

## 6. Security Architecture

### Authentication & Authorization
```
┌──────────────────────────────────────────┐
│          OAuth 2.0 (OIDC)                │
│  Google, GitHub, Microsoft, Custom       │
└────────────────┬─────────────────────────┘
                 ↓
         ┌───────────────┐
         │  JWT Token    │
         │  + Refresh    │
         └───────┬───────┘
                 ↓
    ┌────────────────────────────┐
    │  RBAC with Permissions     │
    │  - admin: full access      │
    │  - instructor: manage      │
    │  - student: view + submit  │
    │  - viewer: read-only       │
    └────────────────────────────┘
```

### Data Protection
- **Upload Validation**: File type, size, malware scan
- **S3 Encryption**: AES-256 at rest, TLS in transit
- **Database**: Row-level security, encrypted sensitive fields
- **API**: Rate limiting, CORS, API key rotation
- **Backups**: Daily encrypted snapshots, 30-day retention
- **Audit Logging**: All data access tracked in PostgreSQL

### Secrets Management
```env
# .env.local
OAUTH_CLIENT_ID=...
OAUTH_CLIENT_SECRET=...
JWT_SECRET=...
DATABASE_URL=postgresql://...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
ENCRYPTION_KEY=...
```

---

## 7. Deployment Strategy

### Frontend (Vercel/Netlify)
```yaml
Framework: Next.js
Build: npm run build
Output: .next/ directory
Environment: Staging, Production
Edge Functions: API routes for light processing
```

### Backend (Cloud Provider)
```yaml
# AWS Option
- EC2 / ECS for Node.js API
- RDS PostgreSQL
- S3 for assets
- CloudFront CDN

# Google Cloud Option
- Cloud Run for Node.js API
- Cloud SQL PostgreSQL
- Cloud Storage for assets
- Cloud CDN

# Azure Option
- App Service for Node.js API
- Azure Database for PostgreSQL
- Azure Blob Storage for assets
- Azure CDN
```

### ETL Pipeline (Cloud)
```yaml
# AWS Option
- Lambda (scheduled) + Step Functions
- Batch for heavy compute
- SNS for notifications

# Google Cloud Option
- Cloud Functions (scheduled) + Workflows
- Dataflow for heavy compute
- Pub/Sub for notifications

# Azure Option
- Durable Functions (scheduled)
- Batch for heavy compute
- Service Bus for notifications
```

### Database Migrations
```bash
# Development
npm run db:migrate
npm run db:seed

# Staging/Production
npm run db:migrate:deploy
# With rollback capability
npm run db:migrate:rollback
```

---

## 8. API Security Checklist

- [x] HTTPS/TLS 1.3+
- [x] CORS properly configured
- [x] Rate limiting (100 req/min per IP)
- [x] Request validation (Zod/Joi)
- [x] SQL injection prevention (ORM)
- [x] XSS protection (Content-Security-Policy)
- [x] CSRF token on state-changing operations
- [x] JWT expires in 15 minutes, refresh in 7 days
- [x] API keys rotated quarterly
- [x] Sensitive data encrypted in transit & at rest
- [x] Audit logging for all operations
- [x] File upload scanning (ClamAV)

---

## 9. Development Workflow

### Local Setup
```bash
# Clone
git clone https://github.com/org/ml-course-platform
cd ml-course-platform

# Backend
cd backend
npm install
cp .env.example .env.local
docker-compose up -d postgres
npm run db:migrate
npm run dev

# Frontend
cd ../frontend
npm install
npm run dev

# ETL (optional, Python 3.10+)
cd ../etl
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m etl.pipeline --dry-run
```

### CI/CD Pipeline
```
Code Commit
    ↓
GitHub Actions Start
    ├─ Lint (ESLint, Prettier)
    ├─ Test (Jest, Pytest)
    ├─ Build (Next.js, Node.js)
    ├─ Security Scan (SAST, Dependency Check)
    └─ Deploy to Staging (on main)
        └─ Manual approval → Deploy to Production
```

---

## 10. Monitoring & Observability

### Metrics
- API response time
- Database query performance
- S3 operations latency
- ETL pipeline duration
- OAuth success rate

### Logging
- Application logs → CloudWatch/Stackdriver
- Audit logs → PostgreSQL
- Error tracking → Sentry/DataDog

### Alerts
- API error rate > 1%
- Database connection pool exhausted
- ETL pipeline failure
- Unauthorized access attempts
- Large file uploads

---

## Cost Optimization

| Service | Estimate | Notes |
|---------|----------|-------|
| PostgreSQL | $50-200/mo | Managed RDS/Cloud SQL |
| S3/Object Storage | $25-100/mo | Based on storage/traffic |
| Backend Hosting | $50-500/mo | Depends on scale |
| Frontend Hosting | Free-50/mo | Vercel has generous free tier |
| ETL Computing | $20-200/mo | Scheduled, light compute |
| **Total** | **~$200-1000/mo** | Scales with usage |

---

## Next Steps
1. ✅ Choose CMS (Strapi vs Sanity)
2. ✅ Set up PostgreSQL database
3. ✅ Implement OAuth authentication
4. ✅ Build core API endpoints
5. ✅ Create ETL pipeline skeleton
6. ✅ Configure S3-compatible storage
7. ✅ Set up GitHub Actions workflows
8. ✅ Implement security measures
9. ✅ Deploy to staging
10. ✅ Load testing & optimization
