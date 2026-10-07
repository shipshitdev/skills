---
name: security-expert
description: Applies OWASP Top 10 security practices to React, Next.js and NestJS code. Use for auth, sensitive data, encryption or hashing, CORS/CSP, or reviewing vulnerabilities.
metadata:
  version: "2.2.4"
  tags: "security, owasp, application-security"
when_to_use: "security headers, multi-tenancy isolation"
---

# Security Expert Skill

## When to Use

- Implementing authentication or authorization
- Reviewing code for security vulnerabilities
- Setting up security configurations
- Handling sensitive data
- Implementing encryption or hashing
- Configuring CORS, CSP, or security headers
- Reviewing dependencies for vulnerabilities
- Implementing multi-tenancy or data isolation

## Project Context Discovery

1. Check `.agents/memory/` for security architecture notes and project facts
2. Review the applicable `AGENTS.override.md` / `AGENTS.md` chain and any explicitly configured fallback instruction file; include `CLAUDE.md` only for Claude-specific rules
3. Identify security patterns and tools
4. Check for `[project]-security-expert` skill

## Core Security Principles

### Authentication & Authorization

**Authentication:** Secure password hashing (bcrypt/argon2), JWT management, session security, MFA, OAuth/SSO

**Authorization:** RBAC, permission checks on all endpoints, resource-level auth, multi-tenancy enforcement

### Input Validation

- DTOs with class-validator
- Sanitize user input
- Prevent SQL injection (typed Prisma client, tagged `$queryRaw` only)
- Parameterized queries

### Data Protection

- Encryption at rest and in transit
- Passwords hashed (never plaintext)
- Environment variables for secrets
- No secrets in code

### Security Headers

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security
- Content Security Policy

## OWASP Top 10 Quick Reference

1. **Broken Access Control:** Verify auth on all endpoints
2. **Cryptographic Failures:** Strong encryption, proper hashing
3. **Injection:** Parameterized queries, input validation
4. **Insecure Design:** Security by design, threat modeling
5. **Security Misconfiguration:** Secure defaults, remove unused features
6. **Vulnerable Components:** Keep dependencies updated
7. **Authentication Failures:** Strong passwords, MFA, brute force protection
8. **Integrity Failures:** Secure CI/CD, code signing
9. **Logging Failures:** Comprehensive logging, monitoring
10. **SSRF:** Validate URLs, whitelist domains

## Security Checklist Summary

- [ ] Passwords hashed (bcrypt/argon2)
- [ ] All endpoints protected
- [ ] Multi-tenancy enforced
- [ ] All inputs validated
- [ ] Encryption at rest/transit
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Dependencies up to date

---

**For complete authentication/authorization patterns, input validation examples, OWASP prevention techniques, framework-specific security (React/Next.js/NestJS), Postgres/Prisma security, AWS security, and detailed security checklists, see:** `references/full-guide.md`
