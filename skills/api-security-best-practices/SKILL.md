---
name: api-security-best-practices
description: "Implement secure API design: authentication (JWT, OAuth 2.0, API keys), authorization (RBAC), input validation, rate limiting, and protection against OWASP API Top 10 vulnerabilities. Use when designing new APIs, securing existing ones, or conducting API security reviews."
license: MIT
metadata:
  version: "1.0.0"
  tags: "security, api, jwt, oauth, rate-limiting, owasp, authentication"
  author: "antigravity-awesome-skills"
---

# API Security Best Practices

Guide for building secure APIs with authentication, authorization, input validation, rate limiting, and protection against common vulnerabilities.

## When to Use

- Designing new API endpoints
- Securing existing APIs
- Implementing authentication and authorization
- Protecting against API attacks (injection, DDoS, abuse)
- Conducting API security reviews or preparing for audits
- Implementing rate limiting and throttling

## Step 1: Authentication & Authorization

### JWT Implementation

```javascript
// Generate secure JWT
const token = jwt.sign(
  { userId: user.id, email: user.email, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: '1h', issuer: 'your-app', audience: 'your-app-users' }
)

// Refresh token for long-lived sessions
const refreshToken = jwt.sign(
  { userId: user.id },
  process.env.JWT_REFRESH_SECRET,
  { expiresIn: '7d' }
)
```

```javascript
// Verify middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization']
  const token = authHeader && authHeader.split(' ')[1] // Bearer TOKEN

  if (!token) return res.status(401).json({ error: 'Access token required' })

  jwt.verify(token, process.env.JWT_SECRET, { issuer: 'your-app' }, (err, user) => {
    if (err?.name === 'TokenExpiredError') return res.status(401).json({ error: 'Token expired' })
    if (err) return res.status(403).json({ error: 'Invalid token' })
    req.user = user
    next()
  })
}
```

**Critical:** Never reveal whether a user exists in error messages. Return `'Invalid credentials'` for both wrong email AND wrong password.

### RBAC

```javascript
const authorize = (...roles) => (req, res, next) => {
  if (!roles.includes(req.user.role)) {
    return res.status(403).json({ error: 'Insufficient permissions' })
  }
  next()
}

app.delete('/api/users/:id', authenticateToken, authorize('admin'), deleteUser)
```

## Step 2: Input Validation & Sanitization

```javascript
import { z } from 'zod'

const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128),
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s'-]+$/),
})

app.post('/api/users', (req, res) => {
  const result = CreateUserSchema.safeParse(req.body)
  if (!result.success) {
    return res.status(400).json({ error: 'Validation failed', details: result.error.issues })
  }
  // Use result.data (typed, validated)
})
```

**Rules:**

- Validate ALL input on the server (never trust client-side validation)
- Use allowlist validation (define what's allowed, reject everything else)
- Parameterize all database queries — never concatenate user input into SQL
- Sanitize outputs to prevent XSS in API responses

## Step 3: Rate Limiting

```javascript
import rateLimit from 'express-rate-limit'

// Global rate limit
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: { error: 'Too many requests, please try again later' },
})

// Strict limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 login attempts per 15 min
  skipSuccessfulRequests: true,
})

app.use('/api/', limiter)
app.use('/api/auth/', authLimiter)
```

## Step 4: Data Protection

```javascript
// Security headers
app.use(helmet())
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }))

// Never expose internal error details
app.use((err, req, res, next) => {
  logger.error({ err, requestId: req.id })
  res.status(500).json({ error: 'Internal server error', requestId: req.id })
  // requestId lets you correlate logs without exposing stack traces
})

// Password hashing
const hash = await bcrypt.hash(password, 12)
const isValid = await bcrypt.compare(password, hash)
```

## OWASP API Top 10 Checklist

| Risk | Prevention |
|------|-----------|
| Broken Object Level Authorization | Check ownership on every object-level operation |
| Broken Authentication | Use JWT with short expiry + refresh tokens |
| Excessive Data Exposure | Use `select` to return only needed fields |
| Lack of Resources & Rate Limiting | Apply rate limiting per endpoint and user |
| Broken Function Level Authorization | RBAC on all sensitive endpoints |
| Mass Assignment | Use explicit allowlists, never `req.body` directly |
| Security Misconfiguration | Helmet headers, CORS allowlist, HTTPS only |
| Injection | Parameterized queries, input validation |
| Improper Asset Management | Version APIs, document and deprecate old versions |
| Insufficient Logging | Log auth events, failures, and suspicious activity |

## API Key Management

```javascript
// Validate API key from header (not query string)
const apiKey = req.headers['x-api-key']
if (!apiKey) return res.status(401).json({ error: 'API key required' })

// Store hashed API keys, not plaintext
const hashedKey = crypto.createHash('sha256').update(apiKey).digest('hex')
const keyRecord = await db.apiKey.findFirst({ where: { keyHash: hashedKey } })

if (!keyRecord || keyRecord.expiresAt < new Date()) {
  return res.status(401).json({ error: 'Invalid or expired API key' })
}
```

## Full Reference

See `references/full-guide.md` for complete examples including OAuth 2.0 flows, refresh token rotation, advanced RBAC patterns, and security testing approaches.

## Limitations

- Use only when task matches API security scope.
- Security reviews should complement, not replace, dedicated penetration testing.
