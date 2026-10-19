---
name: security-expert
description: Applies OWASP Top 10 security practices to React, Next.js and NestJS code. Use for auth, sensitive data, encryption or hashing, CORS/CSP, or reviewing vulnerabilities.
metadata:
  version: "2.2.4"
  tags: "security, owasp, application-security"
when_to_use: "security headers, multi-tenancy isolation"
---

# Security Expert

## When to use

- Implementing authentication or authorization
- Reviewing code for security vulnerabilities
- Setting up security configurations (CORS, CSP, security headers)
- Handling sensitive data; implementing encryption or hashing
- Reviewing dependencies for vulnerabilities
- Implementing multi-tenancy or data isolation

## Project context discovery

1. Check the repo's memory/notes directory (if any) for security architecture notes and project facts.
2. Read the project's `AGENTS.md` / `CLAUDE.md` for security rules.
3. Identify the security patterns and tools already in use.
4. Check for a project-specific security skill and prefer its conventions.

## Core principles

### Authentication and authorization

- **Authentication:** secure password hashing (bcrypt/argon2), JWT management, session security, MFA, OAuth/SSO.
- **Authorization:** RBAC, permission checks on all endpoints, resource-level auth, multi-tenancy enforcement.

### Input validation

- DTOs with class-validator
- Sanitize user input
- Prevent SQL injection: typed Prisma client, tagged `$queryRaw` only
- Parameterized queries

### Data protection

- Encryption at rest and in transit
- Passwords hashed, never plaintext
- Environment variables for secrets; no secrets in code

### Security headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security`
- `Content-Security-Policy`

## OWASP Top 10 quick reference

1. **Broken Access Control:** verify auth on all endpoints
2. **Cryptographic Failures:** strong encryption, proper hashing
3. **Injection:** parameterized queries, input validation
4. **Insecure Design:** security by design, threat modeling
5. **Security Misconfiguration:** secure defaults, remove unused features
6. **Vulnerable Components:** keep dependencies updated
7. **Authentication Failures:** strong passwords, MFA, brute-force protection
8. **Integrity Failures:** secure CI/CD, code signing
9. **Logging Failures:** comprehensive logging, monitoring
10. **SSRF:** validate URLs, allowlist domains

## Checklist

- [ ] Passwords hashed (bcrypt/argon2)
- [ ] All endpoints protected
- [ ] Multi-tenancy enforced
- [ ] All inputs validated
- [ ] Encryption at rest and in transit
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Dependencies up to date

## Full guide

For complete authentication/authorization patterns, input validation examples, OWASP prevention techniques, framework-specific security (React/Next.js/NestJS), Postgres/Prisma security, AWS security and detailed checklists, read `references/full-guide.md`.
