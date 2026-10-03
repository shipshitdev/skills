---
name: clerk-validator
description: "Validates Clerk auth config and flags deprecated patterns: proxy.ts on Next.js 16, ClerkProvider setup. Use before Clerk work or when auditing an auth implementation."
metadata:
  version: "2.2.2"
  tags: "clerk, authentication, validation, nextjs, nestjs"
when_to_use: "after AI generates Clerk code"
---

# Clerk Validator

Validates Clerk authentication configuration and enforces modern Clerk patterns with Next.js 16.

## When This Activates

- Setting up Clerk authentication
- Before any auth implementation work
- Auditing existing Clerk configuration
- After AI generates Clerk code
- CI/CD pipeline validation

## Quick Start

```bash
python3 scripts/validate.py --root .
python3 scripts/validate.py --root . --strict
```

## What Gets Checked

### 1. Package Version

```json
// GOOD: Latest Clerk
"@clerk/nextjs": "^6.0.0"

// BAD: Old version
"@clerk/nextjs": "^4.0.0"
```

### 2. Proxy vs Middleware (Next.js 16)

**GOOD - Next.js 16:**

```typescript
// proxy.ts
import { clerkMiddleware } from "@clerk/nextjs/server";
export default clerkMiddleware();
```

**BAD - Deprecated:**

```typescript
// middleware.ts (deprecated in Next.js 16)
import { authMiddleware } from "@clerk/nextjs";  // DEPRECATED
export default authMiddleware();
```

### 3. ClerkProvider Setup

**GOOD:** wrap the entire app in `<ClerkProvider>` inside `app/layout.tsx`.
**BAD:** placing it in `_app.tsx` (Pages Router, deprecated) or forgetting to
wrap the whole tree.

See `references/full-guide.md` (§ Root Layout with Clerk Components) for the
full layout example.

### 4. Auth Import Patterns

**GOOD - Server-side:**

```typescript
import { auth } from "@clerk/nextjs/server";

export default async function Page() {
  const { userId } = await auth();
  // ...
}
```

**BAD - Old patterns:**

```typescript
// Don't use
import { getAuth } from "@clerk/nextjs/server";  // OLD
import { currentUser } from "@clerk/nextjs";     // Check version
```

### 5. Environment Variables

**Required:**

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

**Optional but recommended:**

```env
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

## Deprecated Patterns

| Deprecated | Replacement |
|------------|-------------|
| `authMiddleware()` | `clerkMiddleware()` |
| `middleware.ts` | `proxy.ts` (Next.js 16) |
| `getAuth()` | `auth()` |
| `@clerk/nextjs` < v5 | `@clerk/nextjs@latest` |
| `_app.tsx` provider | `app/layout.tsx` provider |
| `withClerkMiddleware` | `clerkMiddleware()` |

## Validation Output

```
=== Clerk Validation Report ===
Package Version: @clerk/nextjs@6.0.0 ✓
Configuration: ✓ ClerkProvider  ✓ proxy.ts  ✗ middleware.ts found (deprecated)
Auth Patterns:  ✓ auth()  ✗ authMiddleware() in 1 file (deprecated)
Summary: 2 issues found
```

## Modern Clerk Patterns

### Protected Routes (Server Component)

Call `await auth()`, redirect to `/sign-in` when `userId` is missing, and
render only after that check.

See `references/full-guide.md` (§ Protected Route Example) for the full page.

### Protected Routes (Client Component)

Mark the component `"use client"`, read `{ isLoaded, userId }` from
`useAuth()`, and render a loading/redirect state until both are resolved.

See `references/full-guide.md` (§ Use Auth Hook) for the full component.

### API Routes

Call `await auth()` inside the route handler and return `401` before doing
any work when `userId` is missing.

See `references/full-guide.md` (§ Protected API Route) for the full handler.

### NestJS Guard

Extract the bearer token, verify it with `clerkClient.verifyToken`, and
attach `userId` to the request; return `false`/throw on any failure.

See `references/full-guide.md` (§ Authentication Guard) for the full guard.

## Webhook Configuration

Verify the `svix-id` / `svix-timestamp` / `svix-signature` headers with the
`svix` package against `CLERK_WEBHOOK_SECRET` before trusting the payload;
never process an unverified webhook body.

See `references/full-guide.md` (§ Webhooks (Next.js App Router)) for the full
route handler, and (§ Webhook Handler) for the NestJS controller equivalent.

## CI/CD Integration

```yaml
# .github/workflows/validate.yml
- name: Validate Clerk Config
  run: |
    python3 scripts/validate.py \
      --root . \
      --strict \
      --ci
```

## Integration

- `nextjs-validator` - Validates Next.js 16 (proxy.ts)
- `biome-validator` - Validates linting config
- `git-safety` - Ensures no secrets committed
