# Deployment Guide

Deployment patterns for the full-stack workspace.

---

## Overview

| Project | Platform | URL |
|---------|----------|-----|
| API | Railway/Render/Fly.io | api.yourdomain.com |
| Frontend | Vercel | yourdomain.com |
| Mobile | App Store/Play Store | - |

---

## API Deployment

### Docker

The API includes a Dockerfile. Build it from the workspace root so Bun can read the
workspace lockfile (commit `bun.lock` first):

```bash
docker build -f api/Dockerfile -t api .
```

```dockerfile
FROM oven/bun:1 AS base
WORKDIR /app

# Workspace manifests only, so dependency layers cache until a manifest changes
FROM base AS manifests
COPY package.json bun.lock ./
COPY api/package.json api/package.json
COPY frontend/apps/dashboard/package.json frontend/apps/dashboard/package.json
COPY frontend/packages/package.json frontend/packages/package.json
COPY mobile/package.json mobile/package.json
COPY packages/package.json packages/package.json

# All dependencies of the API workspace, for the build
FROM manifests AS deps
RUN bun install --frozen-lockfile --filter "@myorg/api"

# Production dependencies only, for the runtime image
FROM manifests AS prod-deps
RUN bun install --frozen-lockfile --production --filter "@myorg/api"

# Build. prisma generate needs no DATABASE_URL, so nothing secret is required here.
FROM base AS builder
COPY --from=deps /app/ ./
COPY api ./api
WORKDIR /app/api
RUN bun run build

# Production: only the compiled output and production dependencies.
# The generated Prisma client is compiled into dist/generated, so it ships inside dist.
FROM node:24-slim AS runner
ENV NODE_ENV=production
WORKDIR /app/api
# Bun's isolated installs keep the packages in /app/node_modules and symlink the API's own
# dependencies from /app/api/node_modules, so both folders are needed
COPY --from=prod-deps /app/node_modules /app/node_modules
COPY --from=prod-deps /app/api/node_modules ./node_modules
COPY --from=builder /app/api/dist ./dist
COPY --from=builder /app/api/package.json ./package.json
EXPOSE 3001
CMD ["node", "dist/main.js"]
```

Replace `@myorg` with your `--org`.

The Docker context is the workspace root, so the generated root `.dockerignore` is what
keeps `api/.env` (and every other `.env*` file except `.env.example`), `node_modules`,
`.git` and build output out of the image. Keep it when you edit the Dockerfile, and pass
secrets as runtime environment variables, never as files in the image. The runtime needs Node 22.12+ (the NestJS 12 and
Better Auth packages are ESM and load through `require(esm)`).

### Environment Variables

```bash
# Required
NODE_ENV=production
PORT=3001
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
REDIS_URL=redis://...

# Auth (Better Auth runs inside the API at /api/auth)
BETTER_AUTH_SECRET=...        # openssl rand -base64 32
BETTER_AUTH_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
COOKIE_DOMAIN=.yourdomain.com  # shares the session cookie with the dashboard (see Frontend)

# Optional
SENTRY_DSN=https://...
```

Run `bun run prisma:deploy` (`prisma migrate deploy`) against the production database
before the new API version takes traffic.

### Railway

1. Connect GitHub repo
2. Keep the root directory at the repo root and set the Dockerfile path to `api/Dockerfile`
3. Add environment variables
4. Deploy

### Render

1. Create new Web Service (Docker runtime)
2. Connect GitHub repo
3. Keep the root directory at the repo root and set the Dockerfile path to `api/Dockerfile`
4. Add environment variables

---

## Frontend Deployment

### Vercel

1. Import project from GitHub
2. Set root directory to `frontend/apps/dashboard` and allow source files outside the root
   directory (the app imports `frontend/packages`)
3. Framework: Next.js (auto-detected)
4. Add environment variables
5. Deploy

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

The Better Auth session cookie is set by the API (`api.yourdomain.com`). A host-only
cookie is never sent to `yourdomain.com`, so the dashboard's `proxy.ts` would not see the
session. The generated `auth.service.ts` enables Better Auth's
`advanced.crossSubDomainCookies` whenever the API has a `COOKIE_DOMAIN` environment
variable:

```bash
# API environment
COOKIE_DOMAIN=.yourdomain.com
FRONTEND_URL=https://yourdomain.com          # also the Better Auth trustedOrigins entry
BETTER_AUTH_URL=https://api.yourdomain.com
```

Notes:

- Set `domain` explicitly. When it is omitted Better Auth falls back to the host of
  `BETTER_AUTH_URL` (`api.yourdomain.com`), which does not reach the dashboard.
- Production URLs are https, so Better Auth adds the `__Secure-` cookie prefix;
  `getSessionCookie` in `proxy.ts` accepts both names.
- The browser sends the cookie to the API cross-origin because the client uses
  `credentials: "include"` and the API's CORS allows `FRONTEND_URL` with credentials.
- Locally leave `COOKIE_DOMAIN` unset: `localhost:3000` and `localhost:3001` already share
  cookies (cookies are not isolated by port).
- Alternative without cookie domains: rewrite `/api/auth/*` through the dashboard in
  `next.config.ts` and point `NEXT_PUBLIC_API_URL` at the dashboard origin.

### Multiple Apps

For multiple Next.js apps, create one Vercel project per app and set each project's root
directory to `frontend/apps/<app>` (for example `frontend/apps/dashboard` and
`frontend/apps/admin`). Deploys run from CI, not from a local CLI.

---

## Mobile Deployment

### Expo Build

```bash
cd mobile

# iOS
eas build --platform ios

# Android
eas build --platform android
```

### EAS Configuration

Create `eas.json`:

```json
{
  "cli": {
    "version": ">= 3.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  },
  "submit": {
    "production": {}
  }
}
```

### Environment Variables

```bash
# In app.json or via EAS secrets
EXPO_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: cd api && bun install
      - run: cd api && bun run build
      # Deploy step depends on platform

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: frontend
```

---

## Monitoring

### Sentry

Add to both API and Frontend:

```bash
# API
bun add @sentry/nestjs

# Frontend
bun add @sentry/nextjs
```

### Health Checks

API should expose:

```typescript
@Get("/health")
health() {
  return { status: "ok", timestamp: new Date().toISOString() };
}
```

---

## Database

### Postgres (managed, recommended)

Use a managed Postgres provider (Neon, Supabase, RDS, or a self-hosted instance).

1. **Create the database**
   - Create a project or instance in the region closest to your deployment
   - Create an application role with least privilege (no superuser)

2. **Network Access**
   - Restrict inbound connections to the API's IP range or security group
   - Require TLS (`sslmode=require`)

3. **Get the Connection String**
   - Use the pooled connection string for serverless runtimes, the direct one for migrations

4. **Configure Environment**

   ```env
   DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE?sslmode=require
   ```

   Replace `USERNAME`, `PASSWORD`, `HOST`, and `DATABASE` with your values

5. **Apply Migrations**

   Run `bunx prisma migrate deploy` in the deploy pipeline before the new API version starts. Never run `prisma migrate dev` against a shared or production database.

### Redis (Upstash)

1. Create database
2. Get connection string
3. Add to environment variables

---

## Domain Setup

### DNS Records

```
# API
api.yourdomain.com → CNAME → your-api-platform.com

# Frontend
yourdomain.com → CNAME → cname.vercel-dns.com
www.yourdomain.com → CNAME → cname.vercel-dns.com
```

### SSL

Automatic via platform (Vercel, Railway, etc.)

---

## Checklist

### Before Deploy

- [ ] Environment variables set
- [ ] Database accessible
- [ ] Redis accessible
- [ ] Auth configured
- [ ] CORS configured

### After Deploy

- [ ] Health check passing
- [ ] API docs accessible
- [ ] Auth working
- [ ] Monitoring active
- [ ] Logs accessible
