---
name: docker-expert
description: Writes Dockerfiles, multi-stage builds, and docker-compose setups for NestJS and Next.js apps. Use when containerizing an app or fixing container networking or health checks.
metadata:
  version: "2.2.4"
  tags: "docker, containers, infrastructure"
when_to_use: "volumes, Postgres/Redis containers"
---

# Docker Expert

## When to use

- Dockerfile creation for NestJS or Next.js
- docker-compose configuration
- Container networking and volumes
- Multi-stage build optimization
- Health checks and restart policies
- Postgres/Redis container setup

## Before writing

Match the repo: use its package manager and lockfile (Bun by default, `bun.lock`), its Node/Bun version pin, and its real build/start scripts from `package.json`. Pin base image tags to currently supported versions (verify the current LTS/stable tags rather than copying the ones below). Add a `.dockerignore` (at least `node_modules`, `.git`, `.env*`, build output) and run as a non-root user.

## Dockerfiles

### NestJS multi-stage build (Bun)

```dockerfile
FROM oven/bun:1 AS base
WORKDIR /app

FROM base AS deps
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun run build

FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER bun
EXPOSE 3001
CMD ["bun", "dist/main.js"]
```

### Next.js (Bun)

```dockerfile
FROM oven/bun:1 AS base
WORKDIR /app

FROM base AS deps
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun run build

FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
USER bun
EXPOSE 3000
CMD ["bun", "run", "start"]
```

If the repo uses npm or pnpm instead, swap in `npm ci` / `pnpm install --frozen-lockfile` and the matching Node base image. For smaller Next.js images consider `output: "standalone"`.

## Compose patterns

**Development:** volumes for live reload, mounted source, `restart: unless-stopped`, explicit networks.
**Production:** named volumes for persistence, restart policies, health checks, secrets management.

### Postgres

```yaml
services:
  postgres:
    image: postgres:17   # pin to the version the project uses
    container_name: postgres
    restart: unless-stopped
    ports:
      - "127.0.0.1:5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  app-network:

volumes:
  postgres_data:
```

Credentials come from environment variables or secrets, never literals in the file.

## Health checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

The image must contain `curl` (or use a different probe such as `bun -e` / `wget`).

## Best practices

- Multi-stage builds to reduce image size; order layers for caching.
- Use `.dockerignore`.
- Set restart policies and health checks.
- Mount volumes for persistent data.
- Use networks for service isolation; bind databases to `127.0.0.1` unless remote access is required.
