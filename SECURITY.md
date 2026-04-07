# Security Architecture & Best Practices

## Overview

This document outlines the security measures implemented in the ML Course Platform to protect user data, course content, and system integrity.

---

## 1. Authentication & Authorization

### OAuth 2.0 / OpenID Connect
- **Providers**: Google, GitHub, Microsoft
- **Flow**: Authorization Code with PKCE
- **Benefits**: 
  - No password storage
  - Verified email address from provider
  - User device management via provider

```typescript
// Backend: OAuth callback handler
router.post('/oauth-callback', async (req, res) => {
  const { oauthProvider, oauthId, email } = req.body;
  
  // Find or create user
  let user = await prisma.user.findUnique({ where: { email } });
  if (!user) {
    user = await prisma.user.create({
      data: {
        email,
        oauthProvider,
        oauthId,
        emailVerified: true  // Trusted from provider
      }
    });
  }
  
  // Generate JWT tokens
  const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ userId: user.id }, REFRESH_SECRET, { expiresIn: '7d' });
  
  return { token, refreshToken };
});
```

### JWT Token Management
| Token | Expiry | Storage | Usage |
|-------|--------|---------|-------|
| **Access** | 15 minutes | Memory | API requests |
| **Refresh** | 7 days | HttpOnly Cookie | Token refresh |

#### HttpOnly Cookies (Recommended)
```typescript
res.cookie('refreshToken', refreshToken, {
  httpOnly: true,      // Immune to XSS
  secure: true,        // HTTPS only
  sameSite: 'strict',  // CSRF protection
  maxAge: 7 * 24 * 60 * 60 * 1000  // 7 days
});
```

### Role-Based Access Control (RBAC)

#### User Roles
```
┌─────────────────────────────────────┐
│            Permissions              │
├─────────────────────────────────────┤
│ ✓ create:course                     │
│ ✓ read:course                       │
│ ✓ read:own_upload                   │
│ ✓ update:profile                    │
└─────────────────────────────────────┘
       │                 │              │
       ▼                 ▼              ▼
    ┌─────────┐    ┌──────────┐   ┌────────┐
    │ ADMIN   │    │INSTRUCTOR│   │STUDENT │
    └─────────┘    └──────────┘   └────────┘
      (all)      (manage courses) (read-only)
```

```sql
-- Database structure
CREATE TABLE roles (
  id UUID PRIMARY KEY,
  name VARCHAR UNIQUE,
  permissions JSONB  -- Array of permission names
);

CREATE TABLE user_roles (
  user_id UUID,
  role_id UUID,
  PRIMARY KEY (user_id, role_id)
);
```

#### Middleware Implementation
```typescript
export const requireRole = (...roles: string[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    const hasRole = roles.some(r => req.user?.roles.includes(r));
    if (!hasRole) return res.status(403).json({ error: 'Forbidden' });
    next();
  };
};

// Usage
router.delete('/courses/:id', 
  authMiddleware, 
  requireRole('admin'), 
  courseDeletionHandler
);
```

---

## 2. Data Protection

### Encryption in Transit
- **Protocol**: TLS 1.3+
- **Certificate**: Let's Encrypt (auto-renewed)
- **HSTS**: Enabled (max-age=31536000)

```nginx
# nginx SSL configuration
ssl_protocols TLSv1.3 TLSv1.2;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Encryption at Rest
- **Database**: PostgreSQL with pgcrypto
- **Files**: AES-256 on S3
- **Secrets**: AWS Secrets Manager / Azure Key Vault

```sql
-- PostgreSQL encrypted column example
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT,
  phone_encrypted TEXT,  -- Stored encrypted
  
  CONSTRAINT chk_phone CHECK (
    phone_encrypted IS NULL OR
    length(phone_encrypted) > 0
  )
);

-- Encrypt before insert
INSERT INTO users (email, phone_encrypted)
VALUES ('user@example.com', pgp_sym_encrypt('+1234567890', 'secret_key'));

-- Decrypt when retrieving
SELECT email, pgp_sym_decrypt(phone_encrypted::bytea, 'secret_key') as phone
FROM users;
```

### Field-Level Encryption (Sensitive Data)
```typescript
import crypto from 'crypto';

class DataEncryption {
  private encryptionKey = process.env.ENCRYPTION_KEY;
  
  encrypt(plaintext: string): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', this.encryptionKey, iv);
    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
  }
  
  decrypt(ciphertext: string): string {
    const [iv, encrypted] = ciphertext.split(':');
    const decipher = crypto.createDecipheriv('aes-256-cbc', this.encryptionKey, Buffer.from(iv, 'hex'));
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  }
}
```

### S3 Configuration
```bash
# Enable encryption and versioning
aws s3api put-bucket-encryption \
  --bucket ml-course-assets \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Enable versioning for recovery
aws s3api put-bucket-versioning \
  --bucket ml-course-assets \
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block \
  --bucket ml-course-assets \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

---

## 3. Input Validation & Sanitization

### Request Validation (Zod)
```typescript
import { z } from 'zod';

const CourseSchema = z.object({
  titleEs: z.string().min(1).max(255),
  titleEn: z.string().min(1).max(255),
  descriptionEs: z.string().max(2000).optional(),
  descriptionEn: z.string().max(2000).optional(),
  price: z.number().min(0).max(10000),
  collaborationStatus: z.enum(['open', 'closed', 'archived'])
});

// Before processing
const validData = CourseSchema.parse(req.body);
```

### File Upload Validation
```typescript
const ALLOWED_TYPES = {
  'application/pdf': 'pdf',
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'text/plain': 'txt'
};

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

router.post('/uploads', async (req, res) => {
  const { fileType, fileSize } = req.headers;
  
  // Type check
  if (!ALLOWED_TYPES[fileType]) {
    return res.status(400).json({ error: 'File type not allowed' });
  }
  
  // Size check
  if (fileSize > MAX_FILE_SIZE) {
    return res.status(413).json({ error: 'File too large' });
  }
  
  // Malware scan (ClamAV)
  const isSafe = await scanFile(buffer);
  if (!isSafe) {
    return res.status(400).json({ error: 'File contains malware' });
  }
});
```

### SQL Injection Prevention
- **ORM Used**: Prisma (parameterized queries)
- ❌ **Never**: `db.query('SELECT * FROM users WHERE id = ' + id)`
- ✅ **Always**: `prisma.user.findUnique({ where: { id } })`

### XSS Prevention
```typescript
// Express security headers
app.use(helmet());  // Sets X-Frame-Options, X-Content-Type-Options, etc.

// Content Security Policy
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "https:", "data:"]
  }
}));
```

### CSRF Protection
```typescript
import csrf from 'express-csrf';

// Generate CSRF token for state-changing operations
router.get('/csrf-token', (req, res) => {
  res.json({ token: req.csrfToken() });
});

// Validate CSRF token
router.post('/courses', csrf(), validateCourse, createCourse);
```

---

## 4. API Security

### Rate Limiting
```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,  // requests per window
  message: 'Too many requests',
  skip: (req) => req.user?.roles.includes('premium'),  // Skip for premium users
  keyGenerator: (req) => req.user?.id || req.ip
});

app.use('/api/', limiter);
```

### API Key Management
```typescript
// Rate limit by API key
const apiKeyLimiter = rateLimit({
  keyGenerator: (req) => {
    const apiKey = req.headers['x-api-key'];
    return apiKey || req.ip;
  },
  skip: (req) => !req.headers['x-api-key'],
  max: 1000  // per hour for authenticated keys
});

// Rotation strategy
const rotateApiKey = async (userId: string) => {
  const newKey = generateSecureKey();
  const hashedKey = hash(newKey);
  
  // Invalidate old key
  await prisma.apiKey.updateMany({
    where: { userId, isActive: true },
    data: { isActive: false }
  });
  
  // Create new key
  await prisma.apiKey.create({
    data: {
      userId,
      key: hashedKey,
      expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)  // 90 days
    }
  });
};
```

### CORS Configuration
```typescript
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(','),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 3600
}));
```

---

## 5. Audit Logging & Monitoring

### Comprehensive Audit Trail
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR,        -- 'create:course', 'delete:file'
  resource_type VARCHAR, -- 'course', 'user', 'file'
  resource_id UUID,
  change_details JSONB,
  ip_address INET,
  user_agent TEXT,
  timestamp TIMESTAMP DEFAULT now(),
  
  INDEX idx_user_timestamp (user_id, timestamp),
  INDEX idx_resource (resource_type, resource_id)
);
```

### Example Audit Events
```typescript
await prisma.auditLog.create({
  data: {
    userId: req.user?.id,
    action: 'delete:course',
    resourceType: 'course',
    resourceId: courseId,
    changeDetails: {
      courseName: course.name,
      collaborators: course.collaborators
    },
    ipAddress: req.ip,
    userAgent: req.headers['user-agent']
  }
});
```

### Real-Time Alerts
```typescript
// Alert on suspicious activity
if (await isAnomalousActivity(userId, action)) {
  await sendSecurityAlert({
    userId,
    message: `Unusual activity detected: ${action}`,
    severity: 'high',
    requiresReview: true
  });
}
```

---

## 6. Data Backup & Disaster Recovery

### Automated Backups
```bash
# AWS RDS - Automated daily backups
aws rds modify-db-instance \
  --db-instance-identifier ml-course-db \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"

# S3 versioning and replication
aws s3api put-bucket-replication-configuration \
  --bucket ml-course-assets \
  --replication-configuration '{
    "Role": "arn:aws:iam::ACCOUNT:role/s3-replication",
    "Rules": [{
      "Status": "Enabled",
      "Priority": 1,
      "Destination": {
        "Bucket": "arn:aws:s3:::ml-course-backup",
        "ReplicationTime": { "Status": "Enabled", "Time": {"Minutes": 15}}
      }
    }]
  }'
```

### Recovery Time Objectives (RTO)
| Component | RTO | Story |
|-----------|-----|-------|
| Database | 15 min | 10 most recent snapshots kept |
| Files | 1 hour | S3 versioning + cross-region replica |
| API | 5 min | Multi-region deployment ready |
| Frontend | 5 min | CDN with instant invalidation |

---

## 7. Vulnerability Management

### Dependency Scanning
```bash
# Weekly scan with Snyk
snyk test

# Annual penetration testing
npm audit fix  # Auto-fix when possible
npm audit      # Review remaining issues
```

### SAST/DAST
```yaml
# GitHub Actions security scanning
- codecov/codecov-action
- github/codeql-action
- dependency-check
- Snyk
- SonarQube (optional)
```

### Incident Response
1. **Detection**: Real-time monitoring & alerts
2. **Isolation**: Temporarily disable affected user/resource
3. **Investigation**: Review audit logs & forensic data
4. **Notification**: Alert user within 24 hours
5. **Remediation**: Apply fix & deploy
6. **Post-mortem**: Document & improve processes

---

## 8. Compliance & Standards

### Standards Met
- ✅ **GDPR**: User consent, data portability, right to deletion
- ✅ **CCPA**: Privacy policy, opt-out mechanism
- ✅ **HIPAA**: If containing health data (encrypted, access controls)
- ✅ **SOC 2 Type II**: Audited security controls

### Privacy Policy
- Transparent data collection
- User opt-in for cookies
- Clear data retention policies
- Contact: privacy@company.com

---

## 9. Security Checklist

### Pre-Deployment
- [ ] All dependencies audited & up-to-date
- [ ] Secrets not hardcoded (using Secrets Manager)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] HTTPS/TLS configured
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] CSRF tokens validated
- [ ] Input validation in place
- [ ] Audit logging configured

### Post-Deployment
- [ ] WAF rules configured (AWS WAF, Azure WAF)
- [ ] DDoS protection enabled (AWS Shield, Azure DDoS)
- [ ] Security monitoring active
- [ ] Incident response plan documented
- [ ] Backup tested
- [ ] Penetration testing scheduled
- [ ] Privacy impact assessment completed

---

## 10. Security Contacts

- **Security Issues**: security@company.com
- **Data Breach**: legal@company.com + dpo@company.com
- **Responsible Disclosure**: https://company.com/security.txt

**Do not disclose security vulnerabilities publicly before giving us time to fix them (90 days)**

---

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE/SANS Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- AWS Security Best Practices: https://aws.amazon.com/security/best-practices/
