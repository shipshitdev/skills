# Security Expert - Full Guide

## Core Security Principles

### 1. Authentication & Authorization

**Authentication (Who you are):**

- Secure password hashing (bcrypt, argon2)
- JWT token management
- Session security
- MFA implementation
- OAuth/SSO integration

**Authorization (What you can do):**

- Role-based access control (RBAC)
- Permission checks on all endpoints
- Resource-level authorization
- Multi-tenancy enforcement

**Common Patterns:**

```typescript
// NestJS: Authentication Guard
@UseGuards(AuthGuard)
@Get('/users')
async getUsers(@CurrentUser() user: User) {
  // User is authenticated
}

// NestJS: Role-based Authorization
@UseGuards(AuthGuard, RolesGuard)
@Roles('admin')
@Delete('/users/:id')
async deleteUser(@Param('id') id: string) {
  // User is authenticated AND has admin role
}

// Multi-tenancy enforcement
async findAll(organizationId: string) {
  return this.model.find({
    organization: organizationId,  // Always filter
    isDeleted: false
  });
}
```

### 2. Input Validation & Sanitization

**Always validate and sanitize:**

```typescript
// NestJS: DTO Validation
export class CreateUserDto {
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @IsString()
  @MinLength(8)
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
  password: string;
}

// Sanitize user input
import { sanitize } from 'class-sanitizer';

const sanitized = sanitize(userInput);
```

**Prevent Injection Attacks:**

```typescript
// BAD: NoSQL Injection risk
const query = { [userInput]: value };

// GOOD: Validated input
const query = {
  organization: validatedOrgId,
  email: validatedEmail
};

// BAD: SQL Injection (if using SQL)
const query = `SELECT * FROM users WHERE email = '${email}'`;

// GOOD: Parameterized query
const query = 'SELECT * FROM users WHERE email = ?';
db.query(query, [email]);
```

### 3. Data Protection

**Encryption:**

- Encryption at rest (database)
- Encryption in transit (HTTPS/TLS)
- Sensitive fields encrypted
- Key management secure

**Hashing:**

- Passwords hashed (never plaintext)
- Use bcrypt or argon2
- Salt included
- Appropriate cost factor

**Secrets Management:**

- Environment variables for secrets
- No secrets in code
- `.env` in `.gitignore`
- Use secret management services (AWS Secrets Manager)

### 4. Security Headers

**Essential Headers:**

```typescript
// NestJS: Security headers middleware
app.use(helmet());

// Custom headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
  next();
});
```

**Content Security Policy:**

```typescript
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  })
);
```

### 5. CORS Configuration

```typescript
// GOOD: Restrictive CORS
app.enableCors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
});

// BAD: Allow all origins
app.enableCors({ origin: '*' });
```

### 6. Rate Limiting

```typescript
// NestJS: Throttler
@UseGuards(ThrottlerGuard)
@Throttle(10, 60) // 10 requests per minute
@Get('/api/data')
async getData() {
  return this.dataService.findAll();
}
```

## OWASP Top 10 (2021)

### 1. Broken Access Control

**Prevention:**

- Verify authorization on all endpoints
- Enforce multi-tenancy
- Test for privilege escalation
- Validate user permissions

### 2. Cryptographic Failures

**Prevention:**

- Use strong encryption algorithms
- Hash passwords properly
- Protect sensitive data
- Use HTTPS everywhere

### 3. Injection

**Prevention:**

- Parameterized queries
- Input validation
- Output encoding
- Use ORM/ODM safely

### 4. Insecure Design

**Prevention:**

- Threat modeling
- Security by design
- Security requirements
- Secure architecture

### 5. Security Misconfiguration

**Prevention:**

- Secure defaults
- Remove unnecessary features
- Security headers configured
- Error handling secure

### 6. Vulnerable Components

**Prevention:**

- Keep dependencies updated
- Regular security audits
- Remove unused dependencies
- Monitor security advisories

### 7. Authentication Failures

**Prevention:**

- Strong password policies
- Secure session management
- MFA where possible
- Protect against brute force

### 8. Software and Data Integrity

**Prevention:**

- Secure CI/CD pipeline
- Code signing
- Dependency verification
- Secure update mechanisms

### 9. Security Logging Failures

**Prevention:**

- Comprehensive logging
- Log security events
- Monitor logs
- Alert on suspicious activity

### 10. Server-Side Request Forgery (SSRF)

**Prevention:**

- Validate URLs
- Whitelist allowed domains
- Use URL parsing libraries
- Restrict network access

## Framework-Specific Security

### React/Next.js Security

**XSS Prevention:**

- React automatically escapes
- Avoid `dangerouslySetInnerHTML`
- Sanitize if needed
- Content Security Policy

**Authentication:**

- Secure token storage
- HttpOnly cookies preferred
- Token expiration
- Refresh token rotation

**API Security:**

- Never expose API keys in frontend
- Validate all inputs
- Use HTTPS
- Implement CORS correctly

### NestJS Security

**Guards:**

- Authentication guards
- Authorization guards
- Role-based guards
- Custom guards for complex logic

**Validation:**

- DTOs with class-validator
- Pipes for transformation
- Custom validators
- Global validation pipe

**Error Handling:**

- Generic error messages
- No stack traces in production
- Proper HTTP status codes
- Log errors securely

## MongoDB Security

**Connection Security:**

- Use connection strings (not hardcoded)
- Database user with minimal privileges
- Network access restricted
- Encryption at rest enabled

**Query Security:**

- Validate all inputs
- Use parameterized queries
- Prevent NoSQL injection
- Enforce multi-tenancy

**Index Security:**

- Indexes for performance
- Unique indexes for constraints
- Compound indexes for queries
- Monitor index usage

## AWS Security

**IAM:**

- Least privilege principle
- Role-based access
- Regular access reviews
- MFA for console access

**Network Security:**

- Security groups configured
- VPC isolation
- Private subnets for databases
- Network ACLs

**Secrets Management:**

- AWS Secrets Manager
- Parameter Store for config
- Encrypted at rest
- Rotation enabled

**Monitoring:**

- CloudTrail logging
- CloudWatch monitoring
- Security alerts
- Incident response

## Security Checklist

### Authentication

- [ ] Passwords hashed (bcrypt/argon2)
- [ ] JWT tokens secure
- [ ] Session management secure
- [ ] MFA implemented (if needed)
- [ ] Password policies enforced

### Authorization

- [ ] All endpoints protected
- [ ] Role-based access control
- [ ] Multi-tenancy enforced
- [ ] Resource-level authorization
- [ ] Permission checks present

### Input Validation

- [ ] All inputs validated
- [ ] DTOs with validation
- [ ] Injection prevention
- [ ] XSS prevention
- [ ] CSRF protection

### Data Protection

- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] Secrets in environment variables
- [ ] No hardcoded secrets
- [ ] Secure key management

### Configuration

- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Error handling secure
- [ ] Logging configured

### Dependencies

- [ ] Dependencies up to date
- [ ] Security audits run
- [ ] Vulnerabilities addressed
- [ ] Licenses reviewed

## Best Practices

1. **Security by Design:** Build security in from the start
2. **Defense in Depth:** Multiple layers of security
3. **Least Privilege:** Minimum necessary permissions
4. **Fail Securely:** Default to deny, not allow
5. **Keep Updated:** Regular security updates
6. **Monitor & Alert:** Security monitoring enabled
7. **Regular Audits:** Periodic security reviews
8. **Documentation:** Security patterns documented

## Resources

### OWASP Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

### Framework Security

- NestJS Security: https://docs.nestjs.com/security/authentication
- Next.js Security: https://nextjs.org/docs/app/building-your-application/configuring/security-headers
- React Security: https://react.dev/learn/escape-hatches
