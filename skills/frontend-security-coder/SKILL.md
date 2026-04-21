---
name: frontend-security-coder
description: "Expert in secure frontend coding: XSS prevention, safe DOM manipulation, Content Security Policy, clickjacking protection, secure redirects, authentication token storage, and browser security features. Use when implementing frontend security features or fixing client-side vulnerabilities."
license: MIT
metadata:
  version: "1.0.0"
  tags: "security, frontend, xss, csp, dom, clickjacking, authentication"
  author: "antigravity-awesome-skills"
---

# Frontend Security Coder

Expert frontend security developer specializing in client-side security, XSS prevention, and secure UI patterns.

## When to Use vs Security Auditor

- **This skill:** Hands-on frontend security coding, XSS fixes, CSP configuration, DOM security, secure auth token storage
- **`security-audit` skill:** High-level audits, compliance, threat modeling

## Core Principles

1. **Prefer `textContent` over `innerHTML`** for dynamic content
2. **Sanitize all user-generated content** with DOMPurify before rendering
3. **Never trust the client** — all security-critical checks must be on the server
4. **Validate URLs** before navigation or redirect
5. **Use allowlist validation** for all user inputs

## XSS Prevention

```javascript
// NEVER: innerHTML with user content
element.innerHTML = userInput // XSS vulnerability

// GOOD: textContent for plain text
element.textContent = userInput // Safe

// GOOD: DOMPurify for rich text / HTML
import DOMPurify from 'dompurify'
element.innerHTML = DOMPurify.sanitize(userInput, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
  ALLOWED_ATTR: ['href', 'title', 'target'],
})

// React: JSX is safe by default
<div>{userInput}</div> // Safe — React escapes automatically

// React: dangerouslySetInnerHTML requires sanitization
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }} />
```

## Content Security Policy (CSP)

```javascript
// Meta tag CSP (basic)
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'nonce-{NONCE}'; style-src 'self'; img-src 'self' data: https:">

// Nonce-based CSP for inline scripts
const nonce = crypto.randomBytes(16).toString('base64')
// Set header: Content-Security-Policy: script-src 'self' 'nonce-{nonce}'
<script nonce={nonce}>/* allowed inline script */</script>

// CSP violation reporting
Content-Security-Policy: default-src 'self'; report-uri /csp-report
```

**Goal:** Eliminate `'unsafe-inline'` and `'unsafe-eval'` for scripts.

## Input Validation

```javascript
// Allowlist validation
function validateEmail(email) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
}

// File upload validation
function validateFile(file) {
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
  const MAX_SIZE = 5 * 1024 * 1024 // 5MB

  if (!ALLOWED_TYPES.includes(file.type)) throw new Error('File type not allowed')
  if (file.size > MAX_SIZE) throw new Error('File too large')
}

// URL validation before navigation
function validateRedirectUrl(url) {
  try {
    const parsed = new URL(url, window.location.origin)
    // Only allow same-origin redirects
    if (parsed.origin !== window.location.origin) return false
    return true
  } catch {
    return false
  }
}
```

## Secure Redirects

```javascript
// NEVER: open redirect
const redirectTo = new URLSearchParams(location.search).get('next')
window.location.href = redirectTo // Open redirect vulnerability

// GOOD: validate before redirecting
const redirectTo = new URLSearchParams(location.search).get('next')
if (redirectTo && validateRedirectUrl(redirectTo)) {
  window.location.href = redirectTo
} else {
  window.location.href = '/dashboard' // Safe fallback
}
```

## Authentication Token Storage

```javascript
// AVOID: localStorage for JWTs (vulnerable to XSS)
localStorage.setItem('token', jwt) // If XSS occurs, attacker gets token

// PREFER: HttpOnly cookies (set by server)
// Server sets: Set-Cookie: token=...; HttpOnly; Secure; SameSite=Strict
// No JS access to token — XSS can't steal it

// If using localStorage, accept the XSS risk and mitigate it
// by using short-lived tokens and strict CSP
```

## External Links

```javascript
// Always add noopener noreferrer to external links
<a href="https://external.com" target="_blank" rel="noopener noreferrer">Link</a>

// Without noopener, the opened page can access window.opener
```

## Clickjacking Protection

Apply only in production environments — disable when embedding in iframes during development.

```javascript
// Detect if running in frame
if (window.top !== window.self) {
  // In an iframe — only show UI if expected
  document.body.innerHTML = '<p>This app cannot be embedded.</p>'
}
```

Clickjacking is primarily prevented by server-side headers:

- `X-Frame-Options: DENY` (or `SAMEORIGIN`)
- `Content-Security-Policy: frame-ancestors 'none'`

## Subresource Integrity (SRI)

```html
<!-- Verify external scripts haven't been tampered with -->
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-abc123..."
  crossorigin="anonymous">
</script>
```

## Security Checklist

- [ ] No `innerHTML` with unsanitized user input
- [ ] DOMPurify used for rich text rendering
- [ ] CSP header configured (or meta tag as fallback)
- [ ] External links have `rel="noopener noreferrer"`
- [ ] URL validation before redirects
- [ ] File uploads validated by type and size
- [ ] Auth tokens stored in HttpOnly cookies (not localStorage)
- [ ] SRI hashes on external CDN resources
- [ ] No `document.write()` usage

## Limitations

- Use only when task matches frontend security coding scope.
- CSP should be tested thoroughly — overly strict policies break functionality.
- Security implementation should be reviewed before production deployment.
