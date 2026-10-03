---
name: security-audit
description: Run a self-contained security audit workflow for web applications and APIs, covering scoping, reconnaissance, manual testing, API review, hardening, and reporting. Use when auditing a web app or API for security issues, reviewing auth or session handling, checking input validation and injection risk, or hardening before release.
metadata:
  version: "2.2.2"
  tags: "security, audit, web, api, hardening"
---

# Security Audit

## When to Use

- auditing a web application or API for security issues
- reviewing authentication, authorization, or session handling
- checking input validation, injection risk, or data exposure
- performing a structured hardening and reporting pass before release

## Scope and Safety

- Confirm the target, authorized boundaries, and whether testing is read-only or allows active probing.
- Do not run destructive checks, high-volume fuzzing, or denial-of-service style traffic unless explicitly authorized.
- Record assumptions, environment limits, and access level before starting.
- Prefer reproducible evidence over broad claims.

## Audit Workflow

### Phase 1: Scope and Reconnaissance

1. Identify the in-scope domains, apps, APIs, jobs, and background workers.
2. Map the attack surface:
   - routes and entry points
   - authentication flows
   - admin surfaces
   - file upload or import paths
   - third-party callbacks and webhooks
3. Note the framework, hosting model, data stores, and external integrations.
4. Build a simple asset inventory before testing.

### Phase 2: Baseline Review

1. Check dependency versions, known exposure areas, and obvious misconfigurations.
2. Review environment and deployment assumptions:
   - secret handling
   - logging
   - debug mode
   - CORS
   - cookie flags
   - security headers
3. Identify areas where automated scanning would be useful, but keep the workflow self-contained: describe the scan you would run and why.

### Phase 3: Manual Web Application Testing

Check:

- injection risk in query params, forms, search, filters, uploads, and template rendering
- XSS risk in stored, reflected, and DOM-driven flows
- broken authentication, weak session handling, and insecure password reset flows
- broken access control and IDOR patterns across user, team, and admin scopes
- CSRF exposure on state-changing requests
- path traversal, file handling, and unsafe object access
- sensitive data exposure in UI, logs, client storage, and error messages

For each finding, capture:

- entry point
- required privileges
- reproduction steps
- observed impact
- fix direction

### Phase 4: API Security Review

Check:

- endpoint inventory and undocumented routes
- authn/authz coverage on every state-changing endpoint
- tenant isolation and object-level authorization
- rate limiting and abuse resistance
- request validation and schema enforcement
- unsafe defaults in error responses
- webhook signature verification and replay handling

Where useful, describe the exact request variants that should be tested:

- missing auth
- low-privilege auth
- cross-tenant identifiers
- malformed payloads
- boundary values
- repeated requests

### Phase 5: Hardening Review

Review:

- password and token lifecycle
- MFA or step-up auth where appropriate
- least-privilege roles and admin separation
- audit logging for privileged actions
- secrets management and rotation
- SSRF, open redirect, and outbound request controls
- file upload validation and storage isolation
- backup, recovery, and incident response readiness

### Phase 6: Reporting

Produce a report with:

1. Executive summary
2. Scope and methodology
3. Findings ordered by severity
4. Reproduction notes and evidence
5. Remediation guidance
6. Residual risks and follow-up checks

## Security Checklist

### Web

- [ ] Authentication flows reviewed
- [ ] Authorization boundaries reviewed
- [ ] Session handling reviewed
- [ ] Input validation reviewed
- [ ] Injection risk reviewed
- [ ] XSS risk reviewed
- [ ] CSRF protection reviewed
- [ ] Error handling and data exposure reviewed

### API

- [ ] Endpoint inventory captured
- [ ] Auth coverage checked per endpoint
- [ ] Object-level authorization checked
- [ ] Rate limiting reviewed
- [ ] Validation and schema handling reviewed
- [ ] Webhook verification reviewed

### Operations

- [ ] Secrets handling reviewed
- [ ] Logging and audit trail reviewed
- [ ] Security headers and cookie settings reviewed
- [ ] Dependency posture reviewed
- [ ] Recovery and incident readiness reviewed

## Output Standard

Every finding should include:

- title
- severity
- affected surface
- reproduction steps
- impact
- remediation
- confidence level

## Limits

- This skill structures the audit; it does not replace environment-specific testing or specialist review.
- If access, authorization, or rules of engagement are unclear, stop and clarify before continuing.
