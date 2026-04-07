# ML Course Platform - Complete System Architecture

A production-ready, scalable platform for managing and delivering bilingual machine learning courses with secure content management, automated ETL processing, and role-based access control.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Security](#security)

---

## ✨ Features

### Content Management
- ✅ Bilingual content (Spanish/English)
- ✅ Rich course structure (chapters, figures, code snippets)
- ✅ Support for various content types (PDF, Jupyter, images, code)
- ✅ Automatic content extraction & summarization via ETL pipeline
- ✅ Multi-language translations with Deepl API

### User Management & Security
- ✅ OAuth 2.0 authentication (Google, GitHub, Microsoft)
- ✅ Role-based access control (Admin, Instructor, Student, Viewer)
- ✅ Fine-grained permissions system
- ✅ Comprehensive audit logging
- ✅ Encrypted sensitive data (at rest & in transit)

### Scalability & Performance
- ✅ Serverless architecture (cloud-agnostic)
- ✅ CDN for static assets
- ✅ Database connection pooling
- ✅ API rate limiting & CORS
- ✅ ElasticSearch for fast course search (optional)

### DevOps & CI/CD
- ✅ Automated GitHub Actions workflows
- ✅ Infrastructure as Code (Terraform/Bicep)
- ✅ Docker containerization
- ✅ Multi-environment deployment (Dev, Staging, Prod)
- ✅ Automated security scanning (Snyk, CodeQL)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React, TailwindCSS, TypeScript | Modern SPA with static generation |
| **Backend** | Node.js, Express, Prisma, PostgreSQL | REST API with type-safety |
| **ETL** | Python 3.11, PyMuPDF, spacy, Transformers | Document processing & enrichment |
| **Database** | PostgreSQL 15, pgcrypto | Relational data with encryption |
| **Storage** | AWS S3 / Azure Blob | Scalable file storage |
| **Auth** | OAuth 2.0, JWT, RBAC | Secure identity & permissions |
| **CI/CD** | GitHub Actions, Docker | Automated build & deploy |
| **IaC** | Terraform / Azure Bicep | Infrastructure management |
| **Monitoring** | CloudWatch, Sentry, DataDog | Observability (optional) |

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.10+
- PostgreSQL 14+
- Docker (optional)
- Git & Git LFS

### 1. Clone Repository
```bash
git clone https://github.com/org/ml-course-platform.git
cd ml-course-platform
git lfs pull
```

### 2. Backend Setup (5 minutes)
```bash
cd backend
npm install
cp .env.example .env.local
# Edit .env.local with your values

# Start PostgreSQL
docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15

# Setup database
npm run db:migrate

# Start server
npm run dev
# → http://localhost:3000
```

### 3. Frontend Setup (5 minutes)
```bash
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:3000" > .env.local
npm run dev
# → http://localhost:3001
```

### 4. Optional: ETL Pipeline
```bash
cd ../etl
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m etl.pipeline --course-id test --source ./chapters --dry-run
```

---

## 📁 Project Structure

```
ml-course-platform/
│
├── backend/                      # Node.js/Express API
│   ├── src/
│   │   ├── index.ts             # Main app entry
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth.routes.ts
│   │   │   ├── course.routes.ts
│   │   │   ├── user.routes.ts
│   │   │   └── upload.routes.ts
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts
│   │   │   └── error.middleware.ts
│   │   └── config/
│   ├── prisma/
│   │   ├── schema.prisma        # Database schema
│   │   └── migrations/
│   ├── tests/
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/                     # Next.js application
│   ├── app/
│   │   ├── page.tsx             # Home page
│   │   ├── courses/
│   │   │   ├── page.tsx         # Course list
│   │   │   └── [id]/page.tsx    # Course detail
│   │   └── admin/               # Admin panel
│   ├── components/
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   └── auth.ts              # Auth utilities
│   └── .env.local
│
├── etl/                          # Python ETL pipeline
│   ├── src/
│   │   ├── pipeline.py          # Main orchestrator
│   │   ├── extractors/
│   │   │   ├── pdf_extractor.py
│   │   │   └── notebook_extractor.py
│   │   ├── processors/
│   │   │   ├── nlp_processor.py
│   │   │   └── code_processor.py
│   │   └── loaders/
│   │       ├── database_loader.py
│   │       └── s3_loader.py
│   ├── requirements.txt
│   └── tests/
│
├── infrastructure/               # IaC
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── rds.tf
│   │   ├── s3.tf
│   │   └── variables.tf
│   └── docker/
│       ├── Dockerfile.backend
│       ├── Dockerfile.etl
│       └── docker-compose.yml
│
├── .github/workflows/           # CI/CD
│   ├── ci.yml                   # Lint, test, build
│   ├── etl.yml                  # ETL pipeline trigger
│   └── deploy.yml               # Production deployment
│
├── docs/
│   ├── ARCHITECTURE.md          # System design
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── SECURITY.md              # Security measures
│   ├── API.md                   # API documentation
│   └── CONTRIBUTING.md
│
└── README.md
```

---

## 🏗️ System Architecture

### High-Level Flow
```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│         Vercel/Netlify + CloudFront CDN                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway/WAF                             │
│              Rate Limiting • CORS • Auth                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    ┌──────────────┐       ┌──────────────┐
    │  REST API    │       │  WebSocket   │
    │ (Express)    │       │ (Optional)   │
    └──────┬───────┘       └──────────────┘
           │
      ┌────┴────┬──────────┬───────────┐
      │          │          │           │
      ▼          ▼          ▼           ▼
   ┌─────┐  ┌─────┐  ┌────────┐  ┌──────────┐
   │ JWT │  │Role │  │Audit   │  │Encryption│
   │Valid│  │Check│  │Logs    │  │Module    │
   └─────┘  └─────┘  └────────┘  └──────────┘

   ┌──────────────────────────────────────────┐
   │          PostgreSQL Database             │
   │  users • roles • courses • chapters       │
   │  figures • code_snippets • audit_logs    │
   └──────────────────────────────────────────┘

   ┌──────────────────────────────────────────┐
   │     AWS S3 / Azure Blob Storage          │
   │  figures • code files • course assets     │
   │        (encrypted, versioned)            │
   └──────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  ETL Pipeline (Python)                       │
│  GitHub Repo → Extract → Process → Enrich → Load            │
│  (Scheduled: Daily 2 AM via GitHub Actions)                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
```
Course Author commits to GitHub
    ↓
GitHub Actions triggers CI
    ├─ Lint, test, security scan
    └─ On merge to main → trigger ETL
                            ↓
                    ETL Pipeline starts
                    ├─ Extract PDFs/Notebooks
                    ├─ Process: NLP, summarize
                    ├─ Translate: Deepl API
                    ├─ Upload: Figures to S3
                    └─ Save: Metadata to DB
                            ↓
                    Generate content.json
                    ├─ Push to S3
                    └─ Invalidate CDN
                            ↓
                    Frontend fetches via API
                    ├─ Gets course data
                    ├─ Loads S3 assets
                    └─ Renders to users
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Detailed system design, components, and flows |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | Step-by-step deployment guides (AWS/Azure/GCP) |
| **[SECURITY.md](./SECURITY.md)** | Security architecture, encryption, RBAC |
| **API.md** | OpenAPI documentation (Swagger) |
| **CONTRIBUTING.md** | Development workflow & code standards |

---

## 🔐 Security Highlights

### Authentication & Authorization
- OAuth 2.0 with PKCE (no passwords needed)
- JWT tokens with 15-minute expiry & refresh tokens
- Role-based access control with fine-grained permissions
- Multi-tenant support with course-level roles

### Data Protection
- TLS 1.3 for all traffic
- AES-256 encryption at rest (database & S3)
- Field-level encryption for sensitive data
- Encrypted database backups (30-day retention)

### Threat Prevention
- Input validation (Zod schema)
- SQL injection prevention (ORM + parameterized queries)
- XSS protection (CSP headers, sanitization)
- CSRF protection (tokens on state-changing ops)
- Rate limiting (100 req/15min per IP)
- Malware scanning on file uploads (ClamAV)

### Audit & Monitoring
- Comprehensive audit logging (who, what, when, where)
- Anomaly detection for suspicious activity
- Security scanning in CI/CD (Snyk, CodeQL)
- Breach notification within 24 hours

---

## 🚦 Getting Started with Development

### 1. Start Coding
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes, then test
npm run lint
npm test

# Commit with clear message
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### 2. Create Pull Request
- Link to GitHub issue
- Describe changes clearly
- Request review from team

### 3. Automated Checks
- ✅ CI pipeline runs (lint, test, build)
- ✅ Security scanning (Snyk, CodeQL)
- ✅ Code coverage maintained
- ✅ No merge conflicts

### 4. Code Review & Merge
- Address feedback
- Merge to develop
- Then merge develop → main for release

---

## 🌍 Deployment Environments

### Development
- Local machine
- `.env.local` with test credentials
- Full database/storage resets allowed

### Staging
- Replica of production
- Real data (anonymized)
- Pre-deployment validation

### Production
- Multi-region setup
- Zero-downtime deployments
- Automated backups
- 99.9% SLA target

Deployment: `git push origin main` → Auto-deploy via GitHub Actions

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p99) | < 500ms |
| Database Query | < 100ms |
| Page Load Time | < 2s |
| Uptime | 99.9% |
| Deployment Time | < 5 min |

---

## 📞 Support & Contributing

### Getting Help
- 📖 Check [CONTRIBUTING.md](./CONTRIBUTING.md)
- 🐛 Report bugs via GitHub Issues
- 💬 Discuss features in Discussions
- 🔒 Report security via security@company.com

### Code of Conduct
- Be respectful and inclusive
- Follow git workflow
- Write clear commits
- Test your code
- Document changes

---

## 📄 License

MIT - See LICENSE file

---

## 🎯 Roadmap

### Q2 2024
- [ ] Streamlined course creation UI
- [ ] Student progress tracking
- [ ] Certificate generation

### Q3 2024
- [ ] Community forums
- [ ] Video hosting integration
- [ ] Advanced search (Elasticsearch)

### Q4 2024
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Marketplace for instructors

---

## 📞 Contact

- **Engineering**: engineering@company.com
- **Security**: security@company.com
- **Support**: support@company.com

---

**Happy coding! 🚀**

Last updated: March 27, 2026
