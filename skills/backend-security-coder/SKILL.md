---
name: backend-security-coder
description: "Expert in secure backend coding: input validation, authentication, injection prevention, CSRF protection, database security, API security, secure logging, and secret management. Use when implementing backend security features or reviewing backend code for vulnerabilities."
license: MIT
metadata:
  version: "1.0.0"
  tags: "security, backend, csrf, sql-injection, authentication, owasp"
  author: "antigravity-awesome-skills"
---

# Backend Security Coder

Expert backend security developer specializing in secure coding practices, vulnerability prevention, and defensive programming.

## When to Use vs Security Auditor

- **This skill:** Hands-on backend security coding, API security implementation, database security, authentication coding, vulnerability fixes
- **`security-audit` skill:** High-level audits, compliance assessments, threat modeling, penetration testing planning

## Core Security Principles

1. **Validate all inputs** with allowlist approaches — never trust user input
2. **Parameterize all queries** — never concatenate user input into SQL
3. **Fail securely** — default deny, minimal exposure in errors
4. **Defense in depth** — multiple security layers
5. **Principle of least privilege** — minimal permissions everywhere
6. **Audit logging** — log authentication events and security failures

## Secure Coding Areas

### Input Validation & Sanitization

```typescript
// Allowlist validation with Zod
const UserInput = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).regex(/^[\w\s'-]+$/),
  role: z.enum(['user', 'admin', 'moderator']), // Enum, not freeform
})
```

### SQL Injection Prevention

```typescript
// NEVER: string concatenation
const query = `SELECT * FROM users WHERE email = '${email}'`

// ALWAYS: parameterized queries
const user = await db.query('SELECT * FROM users WHERE email = $1', [email])

// With Prisma (automatically safe)
const user = await prisma.user.findFirst({ where: { email } })
```

### CSRF Protection

```typescript
import csrf from 'csurf'

// For cookie-based auth, use CSRF tokens
app.use(csrf({ cookie: { httpOnly: true, secure: true, sameSite: 'strict' } }))

// For stateless JWT APIs, validate Origin/Referer headers
app.use((req, res, next) => {
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    const origin = req.headers.origin || req.headers.referer
    if (!ALLOWED_ORIGINS.includes(new URL(origin).origin)) {
      return res.status(403).json({ error: 'CSRF validation failed' })
    }
  }
  next()
})
```

### HTTP Security Headers

```typescript
import helmet from 'helmet'

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
}))

// Secure cookie settings
res.cookie('session', token, {
  httpOnly: true,    // No JS access
  secure: true,      // HTTPS only
  sameSite: 'strict', // CSRF protection
  maxAge: 3600000,
})
```

### Secure Error Handling

```typescript
// NEVER expose internal details
app.use((err: Error, req, res, next) => {
  // Log full error internally
  logger.error({ err, path: req.path, userId: req.user?.id })

  // Return generic message to client
  res.status(500).json({
    error: 'An unexpected error occurred',
    requestId: req.id, // For support/correlation only
  })
})

// Exception: validation errors can be specific
if (err instanceof ValidationError) {
  res.status(400).json({ error: err.message, fields: err.fields })
}
```

### Secret Management

```typescript
// NEVER hardcode secrets
const apiKey = 'sk-....' // BAD

// Use environment variables
const apiKey = process.env.STRIPE_SECRET_KEY // GOOD

// For production: use secret managers (AWS Secrets Manager, HashiCorp Vault)
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager'
```

### Database Security

```typescript
// Use dedicated read-only user for read operations
const readDb = createConnection({ user: 'app_readonly', ... })
const writeDb = createConnection({ user: 'app_write', ... })

// Field-level encryption for sensitive data
import { createCipher } from 'crypto'
const encryptedSSN = encrypt(ssn, process.env.ENCRYPTION_KEY)
```

### SSRF Prevention (External Requests)

```typescript
import { URL } from 'url'

const ALLOWED_DOMAINS = ['api.stripe.com', 'api.sendgrid.com']

function validateExternalUrl(url: string): boolean {
  try {
    const parsed = new URL(url)
    if (!['http:', 'https:'].includes(parsed.protocol)) return false
    if (!ALLOWED_DOMAINS.includes(parsed.hostname)) return false
    // Block internal IPs
    if (/^(10|172\.1[6-9]|172\.2\d|172\.3[01]|192\.168|127|0)\./.test(parsed.hostname)) return false
    return true
  } catch {
    return false
  }
}
```

### Audit Logging

```typescript
// Log security events — but never log sensitive data
logger.info({
  event: 'login_success',
  userId: user.id,
  email: user.email, // OK
  ip: req.ip,
  userAgent: req.headers['user-agent'],
  // NEVER: password, token, apiKey
})

logger.warn({
  event: 'login_failure',
  email: req.body.email,
  attempts: failedAttempts,
  ip: req.ip,
})
```

## Security Checklist

- [ ] All inputs validated with allowlist approach
- [ ] All database queries parameterized
- [ ] CSRF protection on state-changing operations
- [ ] Security headers configured (helmet)
- [ ] Cookies set with HttpOnly, Secure, SameSite
- [ ] Error responses don't expose internal details
- [ ] Secrets in environment variables, not code
- [ ] External URL requests validated against allowlist
- [ ] Authentication events logged
- [ ] Rate limiting on auth endpoints

## Limitations

- Use only when task matches backend security coding scope.
- Security implementation should be reviewed by a security professional before production deployment.
