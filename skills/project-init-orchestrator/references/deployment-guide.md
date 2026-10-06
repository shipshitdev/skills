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

The API includes a Dockerfile:

```dockerfile
FROM oven/bun:1 AS base
WORKDIR /app

# Install dependencies
FROM base AS deps
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

# Build
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun run build

# Production
FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3001
CMD ["bun", "run", "start:prod"]
```

### Environment Variables

```bash
# Required
NODE_ENV=production
PORT=3001
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
REDIS_URL=redis://...

# Auth (Clerk)
CLERK_SECRET_KEY=sk_...

# Optional
SENTRY_DSN=https://...
```

### Railway

1. Connect GitHub repo
2. Set root directory to `api/`
3. Add environment variables
4. Deploy

### Render

1. Create new Web Service
2. Connect GitHub repo
3. Set root directory to `api/`
4. Build command: `bun install && bun run build`
5. Start command: `bun run start:prod`

---

## Frontend Deployment

### Vercel

1. Import project from GitHub
2. Set root directory to `frontend/`
3. Framework: Next.js (auto-detected)
4. Add environment variables
5. Deploy

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
```

### Multiple Apps

For multiple NextJS apps, deploy each separately:

```bash
# Dashboard
vercel --cwd frontend/apps/dashboard

# Admin
vercel --cwd frontend/apps/admin
```

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
