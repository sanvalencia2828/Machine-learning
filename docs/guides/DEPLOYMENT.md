# Deployment Guide: ML Course Platform

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [ETL Pipeline Setup](#etl-pipeline-setup)
7. [Security Configuration](#security-configuration)
8. [Monitoring & Alerts](#monitoring--alerts)

---

## Prerequisites

### Tools Required
- Node.js 18+ & npm
- Python 3.10+
- PostgreSQL 14+
- Git & Git LFS
- Docker & Docker Compose (optional)
- AWS CLI / Azure CLI / GCP CLI
- Terraform or Bicep

### Accounts & Services
- GitHub repository
- AWS/Azure/GCP account
- OAuth provider credentials (Google, GitHub, Microsoft)
- Email SMTP service (Gmail, SendGrid, etc.)
- S3 or S3-compatible storage

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/org/ml-course-platform.git
cd ml-course-platform
git lfs pull  # Download large assets
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local with your credentials
nano .env.local

# Start PostgreSQL (Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15

# Setup database
npm run db:generate
npm run db:migrate

# (Optional) Seed initial data
npm run db:seed

# Start backend
npm run dev
# Server runs at http://localhost:3000
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:3000/api
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3001
EOF

# Start development server
npm run dev
# Frontend runs at http://localhost:3001
```

### 4. ETL Pipeline Setup (Optional)
```bash
cd ../etl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm

# Test pipeline
python -m etl.pipeline --course-id test_001 --source ./sample_data --dry-run
```

---

## Database Setup

### PostgreSQL Schema
```bash
cd backend

# Create migrations
npx prisma migrate dev --name initial_schema

# View database
npx prisma studio

# Reset database (dev only)
npx prisma migrate reset
```

### Seeding Initial Data
```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Create roles
  const adminRole = await prisma.role.create({
    data: {
      name: 'admin',
      description: 'Full system access',
      permissions: { create: [
        { name: 'create:course' },
        { name: 'delete:course' },
        { name: 'manage:users' }
      ]}
    }
  });

  const instructorRole = await prisma.role.create({
    data: {
      name: 'instructor',
      description: 'Can create and manage courses',
      permissions: { create: [
        { name: 'create:course' },
        { name: 'update:own_course' }
      ]}
    }
  });

  const studentRole = await prisma.role.create({
    data: {
      name: 'student',
      description: 'Can access courses',
      permissions: { create: [
        { name: 'read:course' }
      ]}
    }
  });

  console.log('Roles created:', { adminRole, instructorRole, studentRole });
}

main().catch(console.error).finally(() => prisma.$disconnect());
```

Run migrations:
```bash
npm run db:seed
```

---

## Backend Deployment

### Option 1: AWS EC2/ECS

#### Deploy to ECS
```bash
cd backend

# Build Docker image
docker build -t ml-course-backend:latest .

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

docker tag ml-course-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ml-course-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ml-course-backend:latest

# Deploy using CloudFormation or Terraform
terraform apply -var="docker_image=<account-id>.dkr.ecr.<region>.amazonaws.com/ml-course-backend:latest"
```

#### RDS PostgreSQL
```hcl
# terraform/rds.tf
resource "aws_db_instance" "postgres" {
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  
  allocated_storage    = 100
  storage_encrypted    = true
  
  db_name              = "ml_course_db"
  username             = "postgres"
  password             = var.db_password  # Use Secrets Manager
  
  multi_az             = true
  backup_retention_period = 30
  
  publicly_accessible  = false
  
  tags = {
    Name = "ml-course-postgres"
  }
}
```

### Option 2: Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name ml-course-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name ml-course-plan \
  --resource-group ml-course-rg \
  --sku B2 --is-linux

# Create web app
az webapp create \
  --resource-group ml-course-rg \
  --plan ml-course-plan \
  --name ml-course-backend \
  --runtime "node|20-lts"

# Deploy from Git
az webapp deployment source config-zip \
  --resource-group ml-course-rg \
  --name ml-course-backend \
  --src deploy.zip

# Configure environment variables
az webapp config appsettings set \
  --resource-group ml-course-rg \
  --name ml-course-backend \
  --settings \
    DATABASE_URL="postgresql://..." \
    JWT_SECRET="$(openssl rand -base64 32)"
```

### Option 3: Google Cloud Run

```bash
# Build image
gcloud builds submit \
  --tag gcr.io/<project>/ml-course-backend:latest

# Deploy to Cloud Run
gcloud run deploy ml-course-backend \
  --image gcr.io/<project>/ml-course-backend:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL="postgresql://..." \
  --allow-unauthenticated
```

### Environment Variables (Production)
```bash
# Secrets Manager / Key Vault / Secrets Store
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET=${RANDOM_SECRET}
REFRESH_TOKEN_SECRET=${ANOTHER_SECRET}
S3_ACCESS_KEY_ID=${AWS_KEY}
S3_SECRET_ACCESS_KEY=${AWS_SECRET}
# ... more secrets
```

---

## Frontend Deployment

### Vercel (Recommended for Next.js)
```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://api.yoursite.com
```

### Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

### Custom Deployment
```bash
# Build static site
npm run build

# Deploy dist/ folder to CDN
aws s3 sync .next/static s3://ml-course-cdn/
```

---

## ETL Pipeline Setup

### Schedule with GitHub Actions
Already configured in `.github/workflows/etl.yml`

### Or: Local Cron Job
```bash
# Linux crontab
0 2 * * * /home/user/ml-course-platform/etl/run_etl.sh ml_course_001

# run_etl.sh
#!/bin/bash
cd /home/user/ml-course-platform/etl
source venv/bin/activate
python -m etl.pipeline --course-id $1 --source ./chapters
```

### Or: Airflow/Prefect
```python
# dags/ml_course_etl.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-course',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG('ml_course_etl', default_args=default_args, schedule_interval='0 2 * * *') as dag:
    
    def run_pipeline():
        from etl.pipeline import CoursePipeline
        pipeline = CoursePipeline()
        return pipeline.run('ml_course_001', './chapters')
    
    process_task = PythonOperator(
        task_id='process_content',
        python_callable=run_pipeline
    )
```

---

## Security Configuration

### HTTPS/TLS
```nginx
# nginx config
server {
    listen 443 ssl http2;
    server_name api.yoursite.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yoursite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yoursite.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### Database Encryption
```bash
# AWS RDS - Enable encryption
aws rds modify-db-instance \
  --db-instance-identifier ml-course-db \
  --storage-encrypted
```

### API Key Rotation
```bash
# Rotate every 90 days
node scripts/rotate-api-keys.js
```

### Secrets Management
```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name db-password \
  --description "Database password" \
  --secret-string 'mypassword'

# Retrieve in code
const secret = await AWS.SecretsManager.getSecretValue({
  SecretId: 'db-password'
}).promise();
```

---

## Monitoring & Alerts

### CloudWatch / Azure Monitor
```typescript
// Backend logging
import { CloudWatchTransport } from 'winston-cloudwatch';

logger.add(new CloudWatchTransport({
  logGroupName: '/aws/ecs/ml-course-backend',
  logStreamName: 'production'
}));
```

### Metrics to Track
- API response time (p50, p99)
- Database query latency
- Error rates by endpoint
- S3 upload/download throughput
- ETL pipeline duration
- User authentication success rate

### Alerts
```yaml
# Prometheus alerting rules
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  annotations:
    summary: "High error rate detected"

- alert: DatabaseLatency
  expr: histogram_quantile(0.95, rate(db_query_duration[5m])) > 1000
  annotations:
    summary: "Database responding slowly"
```

---

## Production Checklist

- [ ] All tests passing (backend, frontend, ETL)
- [ ] Security scan completed (Snyk, CodeQL)
- [ ] Environment variables set in production
- [ ] Database backups automated
- [ ] SSL/TLS certificates valid
- [ ] CDN configured for static assets
- [ ] Rate limiting enabled
- [ ] Logging & monitoring configured
- [ ] Incident response plan documented
- [ ] Load testing completed
- [ ] Disaster recovery plan tested

---

## Troubleshooting

### Database Connection Issues
```bash
# Check connection
psql $DATABASE_URL -c "SELECT 1;"

# Check migration status
npx prisma migrate status

# View logs
docker logs postgres
```

### ETL Pipeline Failures
```bash
# Run with verbose logging
python -m etl.pipeline \
  --course-id ml_course_001 \
  --source ./chapters \
  --verbose

# Check S3 access
aws s3 ls s3://ml-course-assets/
```

### Missing Environment Variables
```bash
# List all required variables
grep -r 'process.env\.' backend/src | grep -oP "process\.env\.\K[A-Z_]+" | sort -u
```

---

## Support & Escalation

- Backend Issues: Check `/api/health` endpoint
- Database Issues: Contact DBA or check RDS console
- S3/Storage Issues: Check AWS IAM policies
- ETL Pipeline Issues: Check GitHub Actions logs
- Security Issues: Report to security@company.com

