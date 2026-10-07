---
name: docker-expert
description: Writes Dockerfiles, multi-stage builds, and docker-compose setups for NestJS and Next.js apps. Use when containerizing an app or fixing container networking or health checks.
metadata:
  version: "2.2.4"
  tags: "docker, containers, infrastructure"
when_to_use: "volumes, Postgres/Redis containers"
---

# Docker Expert

## When to Use

- Dockerfile creation for NestJS/Next.js
- docker-compose configuration
- Container networking and volumes
- Multi-stage builds optimization
- Health checks and restart policies
- Postgres/Redis container setup

## Dockerfile Best Practices

### NestJS Multi-Stage Build

```dockerfile
FROM node:20-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package*.json ./
RUN npm ci

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3001
CMD ["node", "dist/main.js"]
```

### Next.js Dockerfile

```dockerfile
FROM node:20-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package*.json ./
RUN npm ci

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

## Docker Compose Patterns

### Development Setup

- Use volumes for live reload
- Mount source code
- Set restart: unless-stopped
- Configure networks

### Production Setup

- Use named volumes for persistence
- Set restart policies
- Configure health checks
- Use secrets management

### Postgres with Docker Compose

```yaml
services:
  postgres:
    image: postgres:17
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

volumes:
  postgres_data:
```

## Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Best Practices

- Use multi-stage builds to reduce image size
- Leverage layer caching
- Use .dockerignore
- Set appropriate restart policies
- Use health checks for containers
- Mount volumes for persistent data
- Use networks for service isolation
