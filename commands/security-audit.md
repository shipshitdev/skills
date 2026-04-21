# Security Audit - Security Scanning Command

Comprehensive security audit covering dependencies, code patterns, configuration, and OWASP Top 10.

## When to Use

- Before deploying to production
- After adding new dependencies
- Regular security reviews
- After security incidents

## Context Discovery

Before auditing, discover the actual project setup:

1. Framework and runtime (React, Next.js, Electron, Node, etc.)
2. Authentication system (Clerk, Auth0, custom JWT, etc.)
3. Database (PostgreSQL/RDS, SQLite, etc.)
4. Package manager (`bun.lock` = Bun)

**Adapt all checks to discovered stack.**

## Phase 1: Dependency Security

```bash
# Bun projects
bun audit 2>/dev/null || bun pm ls --all | head -50

# Check for outdated packages
bun outdated
```

Review `package.json` for known-vulnerable packages. Check advisories.

## Phase 2: Code Security Patterns

### Authentication & Authorization

- All API/IPC endpoints protected
- Auth guards applied consistently
- JWT/session management secure
- No hardcoded credentials

### Input Validation

- DTOs / schemas validate all input
- SQL injection prevention (parameterized queries)
- XSS prevention (React auto-escapes, but check `dangerouslySetInnerHTML`)
- CSRF protection where applicable

### Secrets Management

- No hardcoded secrets in code
- `.env` files in `.gitignore`
- No secrets in git history (`git log -p --all -S 'sk-' | head`)
- Environment variables used for all credentials

### Electron-Specific (desktop apps)

- `nodeIntegration: false` in BrowserWindow
- `contextIsolation: true`
- Preload scripts minimize exposed APIs
- No `shell.openExternal` with unvalidated URLs
- IPC handlers validate all arguments

## Phase 3: Configuration Security

- CORS restrictive (not `*`)
- Rate limiting on public endpoints
- HTTPS enforced in production
- Security headers configured (CSP, HSTS, X-Frame-Options)
- Error messages don't leak internals

## Phase 4: Database Security

### PostgreSQL / AWS RDS

- Connection string not hardcoded
- DB user has minimal privileges
- Network access restricted (VPC/security groups)
- SSL connections enforced
- Parameterized queries only

### SQLite (Electron)

- DB file permissions appropriate
- No user input in raw SQL
- Prepared statements used

## OWASP Top 10 Quick Check

1. **Broken Access Control** — auth on all endpoints, role checks
2. **Cryptographic Failures** — proper hashing, encryption in transit/rest
3. **Injection** — parameterized queries, input validation
4. **Insecure Design** — threat model reviewed
5. **Security Misconfiguration** — defaults changed, headers set
6. **Vulnerable Components** — deps audited and updated
7. **Auth Failures** — strong password policy, session management
8. **Data Integrity** — CI/CD security, signed artifacts
9. **Logging Failures** — audit logs exist, no secrets in logs
10. **SSRF** — URL validation, network access restricted

## Output Format

```
SECURITY AUDIT REPORT

Project: [name]
Stack: [discovered]
Date: [date]

SUMMARY
- Critical: N
- High: N
- Medium: N

CRITICAL ISSUES
1. [Issue] — File: [path:line], Fix: [how]

HIGH PRIORITY
1. [Issue] — File: [path:line], Fix: [how]

STRENGTHS
- [what's already good]

RECOMMENDATIONS
[prioritized next steps]
```

## Checklist

- [ ] Discover project stack
- [ ] Audit dependencies
- [ ] Scan code for hardcoded secrets
- [ ] Review auth/authz patterns
- [ ] Check input validation
- [ ] Review configuration security
- [ ] Check database security
- [ ] OWASP Top 10 walkthrough
- [ ] Report with prioritized findings
