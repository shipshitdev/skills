# EC2 Backend Deployment Guide

Complete guide for deploying NestJS, Next.js, and Express backends to EC2 instances using Docker, GitHub Actions, and secure access via Tailscale.

---

## Table of Contents

1. [Project Context Discovery](#project-context-discovery)
2. [Docker Setup](#docker-setup)
3. [Container Registry Setup](#container-registry-setup)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [EC2 Deployment Process](#ec2-deployment-process)
6. [Multi-Service Deployment](#multi-service-deployment)
7. [Security Best Practices](#security-best-practices)
8. [Monitoring and Health Checks](#monitoring-and-health-checks)
9. [Rollback Procedures](#rollback-procedures)
10. [Docker Cleanup and Maintenance](#docker-cleanup-and-maintenance)
11. [Troubleshooting](#troubleshooting)
12. [Checklist](#checklist)

---

## Project Context Discovery

Before setting up deployment, gather information about your project.

### Questions to Answer

1. **Framework**: NestJS, Next.js, or Express?
2. **Package Manager**: npm, yarn, pnpm, or bun?
3. **Node Version**: What version does the project require?
4. **Build Output**: Where does the build output go (`dist/`, `.next/`, `build/`)?
5. **Port**: What port does the application listen on?
6. **Environment Variables**: What secrets/config are needed?
7. **Health Endpoint**: Does the app have a health check endpoint?
8. **Database**: PostgreSQL (Prisma), Redis connections?

### Discovery Commands

```bash
# Check package.json for framework and scripts
cat package.json | jq '.dependencies, .scripts'

# Check for existing Dockerfile
ls -la Dockerfile* docker-compose*

# Check Node version
cat .nvmrc 2>/dev/null || cat package.json | jq '.engines.node'

# Check existing CI workflows
ls -la .github/workflows/
```

---

## Docker Setup

### Multi-Stage Dockerfile: NestJS

```dockerfile
# ============================================
# Stage 1: Base
# ============================================
FROM node:20-alpine AS base
WORKDIR /app

# Install dependencies for native modules
RUN apk add --no-cache libc6-compat

# ============================================
# Stage 2: Dependencies
# ============================================
FROM base AS deps

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# ============================================
# Stage 3: Builder
# ============================================
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# ============================================
# Stage 4: Production
# ============================================
FROM base AS runner

# Set production environment
ENV NODE_ENV=production

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nestjs

# Copy built application
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nestjs:nodejs /app/package.json ./package.json

# Switch to non-root user
USER nestjs

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start application
CMD ["node", "dist/main.js"]
```

### Multi-Stage Dockerfile: Next.js (Standalone)

```dockerfile
# ============================================
# Stage 1: Base
# ============================================
FROM node:20-alpine AS base
WORKDIR /app

RUN apk add --no-cache libc6-compat

# ============================================
# Stage 2: Dependencies
# ============================================
FROM base AS deps

COPY package.json package-lock.json* ./
RUN npm ci

# ============================================
# Stage 3: Builder
# ============================================
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build with standalone output
RUN npm run build

# ============================================
# Stage 4: Production
# ============================================
FROM base AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "server.js"]
```

**Note**: For Next.js standalone, add to `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};

module.exports = nextConfig;
```

### Multi-Stage Dockerfile: Express

```dockerfile
# ============================================
# Stage 1: Base
# ============================================
FROM node:20-alpine AS base
WORKDIR /app

RUN apk add --no-cache libc6-compat

# ============================================
# Stage 2: Dependencies
# ============================================
FROM base AS deps

COPY package.json package-lock.json* ./
RUN npm ci

# ============================================
# Stage 3: Builder (for TypeScript)
# ============================================
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# If using TypeScript
RUN npm run build

# ============================================
# Stage 4: Production
# ============================================
FROM base AS runner

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 express

# Copy production dependencies only
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder --chown=express:nodejs /app/dist ./dist
COPY --from=builder --chown=express:nodejs /app/package.json ./package.json

USER express

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "dist/index.js"]
```

### Dockerfile with Bun

```dockerfile
# ============================================
# Stage 1: Base
# ============================================
FROM oven/bun:1 AS base
WORKDIR /app

# ============================================
# Stage 2: Dependencies
# ============================================
FROM base AS deps

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# ============================================
# Stage 3: Builder
# ============================================
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun run build

# ============================================
# Stage 4: Production
# ============================================
FROM base AS runner

ENV NODE_ENV=production

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3001

CMD ["bun", "run", "start:prod"]
```

### .dockerignore

```
# Dependencies
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build output
dist
.next
build

# Development
.git
.gitignore
*.md
.env*
.env.local
.env.*.local

# IDE
.idea
.vscode
*.swp
*.swo

# Testing
coverage
.nyc_output
*.test.ts
*.spec.ts
__tests__

# Docker
Dockerfile*
docker-compose*
.docker

# CI/CD
.github
.gitlab-ci.yml

# OS
.DS_Store
Thumbs.db
```

---

## Container Registry Setup

### GitHub Container Registry (ghcr.io) - Recommended

**Advantages**:

- Free for public repos
- Integrated with GitHub Actions
- No separate authentication setup

**Setup**:

1. Enable improved container support in repository settings
2. Ensure `GITHUB_TOKEN` has `packages: write` permission

**Image naming**:

```
ghcr.io/<owner>/<repo>:<tag>
ghcr.io/myorg/api:latest
ghcr.io/myorg/api:v1.2.3
ghcr.io/myorg/api:sha-abc1234
```

### AWS ECR

**Setup**:

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name my-api \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

**GitHub Actions Setup**:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2
```

**Image naming**:

```
<account-id>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>
123456789012.dkr.ecr.us-east-1.amazonaws.com/my-api:latest
```

### Docker Hub

**Setup**:

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**Image naming**:

```
<username>/<repo>:<tag>
myuser/my-api:latest
```

---

## CI/CD Pipeline

### Complete GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy to EC2

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'production'
        type: choice
        options:
          - staging
          - production

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================
  # Job 1: Build and Push Docker Image
  # ============================================
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
      image_digest: ${{ steps.build.outputs.digest }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64

  # ============================================
  # Job 2: Deploy to EC2
  # ============================================
  deploy:
    name: Deploy to EC2
    runs-on: ubuntu-latest
    needs: build
    environment: production

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Tailscale
        uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci

      - name: Deploy to EC2
        uses: appleboy/ssh-action@v1.0.3
        env:
          REGISTRY: ${{ env.REGISTRY }}
          IMAGE_NAME: ${{ env.IMAGE_NAME }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          envs: REGISTRY,IMAGE_NAME,GITHUB_TOKEN
          script: |
            set -e

            # Login to container registry
            echo "$GITHUB_TOKEN" | docker login ghcr.io -u ${{ github.actor }} --password-stdin

            # Navigate to deployment directory
            cd /home/${{ secrets.EC2_USER }}/app

            # Pull latest image
            docker compose pull

            # Deploy with zero-downtime
            docker compose up -d --remove-orphans

            # Wait for health check
            sleep 10

            # Verify deployment
            if ! docker compose exec -T api curl -sf http://localhost:3001/health > /dev/null; then
              echo "Health check failed! Rolling back..."
              docker compose rollback 2>/dev/null || docker compose down
              exit 1
            fi

            # Cleanup old images
            docker image prune -af --filter "until=24h"

            echo "Deployment successful!"

      - name: Verify Deployment
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Workflow with Build Args and Secrets

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    build-args: |
      NODE_VERSION=20
      BUILD_DATE=${{ github.event.head_commit.timestamp }}
      GIT_SHA=${{ github.sha }}
    secrets: |
      "npm_token=${{ secrets.NPM_TOKEN }}"
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Monorepo Workflow (Multiple Services)

```yaml
name: Deploy Monorepo Services

on:
  push:
    branches: [main]
    paths:
      - 'apps/api/**'
      - 'apps/worker/**'
      - 'packages/**'

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      worker: ${{ steps.filter.outputs.worker }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'apps/api/**'
              - 'packages/**'
            worker:
              - 'apps/worker/**'
              - 'packages/**'

  build-api:
    needs: changes
    if: ${{ needs.changes.outputs.api == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build API
        uses: docker/build-push-action@v5
        with:
          context: .
          file: apps/api/Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/api:latest

  build-worker:
    needs: changes
    if: ${{ needs.changes.outputs.worker == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Worker
        uses: docker/build-push-action@v5
        with:
          context: .
          file: apps/worker/Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/worker:latest

  deploy:
    needs: [build-api, build-worker]
    if: always() && (needs.build-api.result == 'success' || needs.build-worker.result == 'success')
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        # ... deployment steps
```

---

## EC2 Deployment Process

### Initial EC2 Setup

```bash
#!/bin/bash
# ec2-setup.sh - Run on fresh EC2 instance

set -e

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install Docker Compose v2
sudo apt-get install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Create app directory
mkdir -p ~/app
cd ~/app

# Set up environment file
cat > .env << 'EOF'
NODE_ENV=production
PORT=3001
# Add your environment variables here
EOF

# Secure the .env file
chmod 600 .env

echo "EC2 setup complete! Log out and back in for Docker group to take effect."
```

### Tailscale Setup on EC2

```bash
#!/bin/bash
# Install Tailscale on EC2

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate (interactive - opens browser URL)
sudo tailscale up --ssh

# Verify connection
tailscale status

# Get Tailscale IP for GitHub Secrets
tailscale ip -4
```

**Tailscale OAuth Setup for CI/CD**:

1. Go to Tailscale Admin Console
2. Navigate to Settings > Keys
3. Create OAuth client with:
   - Tags: `tag:ci`
   - Scopes: `devices:read`, `devices:write`
4. Add to GitHub Secrets:
   - `TS_OAUTH_CLIENT_ID`
   - `TS_OAUTH_SECRET`

### Docker Compose for EC2

```yaml
# docker-compose.yml (on EC2)
version: "3.8"

services:
  api:
    image: ghcr.io/myorg/api:latest
    container_name: api
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Deployment Script

```bash
#!/bin/bash
# deploy.sh - Manual deployment script for EC2

set -e

APP_DIR="${APP_DIR:-/home/ubuntu/app}"
HEALTH_URL="${HEALTH_URL:-http://localhost:3001/health}"
MAX_RETRIES=30
RETRY_INTERVAL=2

cd "$APP_DIR"

echo "=== Starting deployment ==="

# Pull latest images
echo "Pulling latest images..."
docker compose pull

# Store current image for rollback
CURRENT_IMAGE=$(docker compose images -q api 2>/dev/null || echo "")

# Deploy new version
echo "Starting new containers..."
docker compose up -d --remove-orphans

# Wait for health check
echo "Waiting for health check..."
for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
    echo "Health check passed!"
    break
  fi

  if [ $i -eq $MAX_RETRIES ]; then
    echo "Health check failed after $MAX_RETRIES attempts"

    # Rollback if we have a previous image
    if [ -n "$CURRENT_IMAGE" ]; then
      echo "Rolling back to previous version..."
      docker compose down
      # Manual rollback would require tagging strategy
    fi

    exit 1
  fi

  echo "Attempt $i/$MAX_RETRIES - waiting ${RETRY_INTERVAL}s..."
  sleep $RETRY_INTERVAL
done

# Cleanup
echo "Cleaning up old images..."
docker image prune -af --filter "until=24h"

echo "=== Deployment complete ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## Multi-Service Deployment

### Docker Compose with Multiple Services

```yaml
# docker-compose.yml
version: "3.8"

services:
  # API Service
  api:
    image: ghcr.io/myorg/api:${API_VERSION:-latest}
    container_name: api
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network

  # Worker Service
  worker:
    image: ghcr.io/myorg/worker:${WORKER_VERSION:-latest}
    container_name: worker
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy
      api:
        condition: service_healthy
    networks:
      - app-network

  # Redis (Queue/Cache)
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - app-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      api:
        condition: service_healthy
    networks:
      - app-network

volumes:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:3001;
    }

    server {
        listen 80;
        server_name api.example.com;

        location / {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
```

---

## Security Best Practices

### 1. Non-Root User in Docker

```dockerfile
# Always run as non-root
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

USER appuser
```

### 2. Secrets Management

**Never commit secrets to Docker images**. Use:

```yaml
# docker-compose.yml with secrets
services:
  api:
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    external: true  # Created with: docker secret create api_key ./key.txt
```

### 3. BuildKit Secrets for Build-Time

```dockerfile
# Dockerfile
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm ci
```

```yaml
# GitHub Actions
- name: Build with secrets
  uses: docker/build-push-action@v5
  with:
    secrets: |
      npm_token=${{ secrets.NPM_TOKEN }}
```

### 4. Environment Variable Security

```bash
# .env file permissions
chmod 600 .env

# Never expose in logs
docker compose config  # Check for exposed secrets
```

### 5. Network Security

```yaml
# Restrict container networking
services:
  api:
    networks:
      - frontend  # External access
      - backend   # Internal only

  database:
    networks:
      - backend   # No external access

networks:
  frontend:
  backend:
    internal: true  # No external access
```

### 6. SSH Key Security

```bash
# Generate dedicated deployment key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f deploy_key

# Add public key to EC2
cat deploy_key.pub >> ~/.ssh/authorized_keys

# Add private key to GitHub Secrets as EC2_SSH_KEY
```

### 7. Tailscale ACL Rules

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["tag:ci"],
      "dst": ["tag:server:22"]
    }
  ],
  "tagOwners": {
    "tag:ci": ["autogroup:admin"],
    "tag:server": ["autogroup:admin"]
  }
}
```

---

## Monitoring and Health Checks

### Health Check Endpoint (NestJS)

```typescript
// health.controller.ts
import { Controller, Get } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckService,
  PrismaHealthIndicator,
} from '@nestjs/terminus';
import { PrismaService } from '../prisma/prisma.service';

@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private prismaHealth: PrismaHealthIndicator,
    private prisma: PrismaService,
  ) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.prismaHealth.pingCheck('database', this.prisma),
    ]);
  }

  @Get('live')
  live() {
    return { status: 'ok', timestamp: new Date().toISOString() };
  }

  @Get('ready')
  @HealthCheck()
  ready() {
    return this.health.check([
      () => this.prismaHealth.pingCheck('database', this.prisma),
    ]);
  }
}
```

### Health Check Endpoint (Express)

```typescript
// health.ts
import { Router } from 'express';
import { PrismaPg } from '@prisma/adapter-pg';
import { PrismaClient } from './generated/prisma/client';

const router = Router();
const prisma = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
});

async function databaseStatus(): Promise<'connected' | 'disconnected'> {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return 'connected';
  } catch {
    return 'disconnected';
  }
}

router.get('/health', async (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    checks: {
      database: await databaseStatus(),
    },
  };

  const isHealthy = health.checks.database === 'connected';
  res.status(isHealthy ? 200 : 503).json(health);
});

export default router;
```

### Docker Compose Health Checks

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### External Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Health monitoring script

HEALTH_URL="${1:-http://localhost:3001/health}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

check_health() {
  APP_DIR="${APP_DIR:-.}"
  mkdir -p "$APP_DIR/.tmp"
  response=$(curl -sf -w "%{http_code}" "$HEALTH_URL" -o "$APP_DIR/.tmp/health_response.json" 2>/dev/null)

  if [ "$response" = "200" ]; then
    echo "$(date): Health check passed"
    return 0
  else
    echo "$(date): Health check failed (HTTP $response)"

    if [ -n "$SLACK_WEBHOOK" ]; then
      curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Health check failed for '"$HEALTH_URL"'"}' \
        "$SLACK_WEBHOOK"
    fi

    return 1
  fi
}

check_health
```

### CloudWatch Integration (AWS)

```yaml
# docker-compose.yml with CloudWatch logging
services:
  api:
    logging:
      driver: awslogs
      options:
        awslogs-region: us-east-1
        awslogs-group: /ecs/api
        awslogs-stream-prefix: api
```

---

## Rollback Procedures

### Automatic Rollback in CI/CD

```yaml
- name: Deploy with Rollback
  uses: appleboy/ssh-action@v1.0.3
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ${{ secrets.EC2_USER }}
    key: ${{ secrets.EC2_SSH_KEY }}
    script: |
      set -e
      cd /home/${{ secrets.EC2_USER }}/app

      # Store current image digest for rollback
      CURRENT_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' api 2>/dev/null || echo "")
      echo "$CURRENT_DIGEST" > .rollback_image

      # Deploy new version
      docker compose pull
      docker compose up -d

      # Health check with timeout
      HEALTHY=false
      for i in {1..30}; do
        if curl -sf http://localhost:3001/health > /dev/null; then
          HEALTHY=true
          break
        fi
        sleep 2
      done

      if [ "$HEALTHY" = false ]; then
        echo "Deployment failed! Rolling back..."

        if [ -n "$CURRENT_DIGEST" ] && [ -f .rollback_image ]; then
          ROLLBACK_IMAGE=$(cat .rollback_image)
          docker compose down

          # Update compose file with rollback image
          sed -i "s|image:.*api:.*|image: $ROLLBACK_IMAGE|" docker-compose.yml
          docker compose up -d

          echo "Rolled back to: $ROLLBACK_IMAGE"
        fi

        exit 1
      fi

      echo "Deployment successful!"
```

### Manual Rollback Script

```bash
#!/bin/bash
# rollback.sh - Manual rollback script

APP_DIR="${APP_DIR:-/home/ubuntu/app}"
cd "$APP_DIR"

echo "=== Available images ==="
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}" | grep -E "api|worker"

echo ""
read -p "Enter image tag to rollback to (e.g., sha-abc1234): " ROLLBACK_TAG

if [ -z "$ROLLBACK_TAG" ]; then
  echo "No tag provided. Exiting."
  exit 1
fi

# Update docker-compose.yml with rollback tag
export API_VERSION="$ROLLBACK_TAG"

echo "Rolling back to: $ROLLBACK_TAG"
docker compose up -d

# Verify
sleep 10
if curl -sf http://localhost:3001/health > /dev/null; then
  echo "Rollback successful!"
else
  echo "Rollback may have failed. Check logs:"
  docker compose logs --tail=50
fi
```

### Blue-Green Deployment

```yaml
# docker-compose.blue-green.yml
version: "3.8"

services:
  api-blue:
    image: ghcr.io/myorg/api:${BLUE_VERSION:-latest}
    container_name: api-blue
    ports:
      - "3001:3001"
    profiles:
      - blue

  api-green:
    image: ghcr.io/myorg/api:${GREEN_VERSION:-latest}
    container_name: api-green
    ports:
      - "3002:3001"
    profiles:
      - green

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

```bash
# Deploy green, then switch
docker compose --profile green up -d
# Test green at :3002
# Update nginx to point to green
# docker compose --profile blue down
```

---

## Docker Cleanup and Maintenance

### Automated Cleanup Script

```bash
#!/bin/bash
# docker-cleanup.sh - Run via cron

set -e

echo "=== Docker Cleanup $(date) ==="

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images (older than 24h)
echo "Removing unused images..."
docker image prune -af --filter "until=24h"

# Remove unused volumes (careful!)
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Remove build cache
echo "Removing build cache..."
docker builder prune -af --filter "until=24h"

# Show disk usage
echo ""
echo "=== Disk Usage ==="
docker system df

echo ""
echo "=== Running Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
```

### Cron Setup for Cleanup

```bash
# Add to crontab (crontab -e)
# Run cleanup daily at 3 AM
0 3 * * * /home/ubuntu/scripts/docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1
```

### Cleanup in CI/CD

```yaml
- name: Post-deployment cleanup
  uses: appleboy/ssh-action@v1.0.3
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ${{ secrets.EC2_USER }}
    key: ${{ secrets.EC2_SSH_KEY }}
    script: |
      # Remove dangling images
      docker image prune -f

      # Remove images older than 7 days, keep last 3 versions
      docker images --format "{{.Repository}}:{{.Tag}}" | \
        grep "ghcr.io/${{ github.repository }}" | \
        tail -n +4 | \
        xargs -r docker rmi || true
```

### Disk Space Monitoring

```bash
#!/bin/bash
# check-disk.sh

THRESHOLD=80
USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')

if [ "$USAGE" -gt "$THRESHOLD" ]; then
  echo "WARNING: Disk usage at ${USAGE}%"

  # Auto-cleanup if critical
  if [ "$USAGE" -gt 90 ]; then
    echo "CRITICAL: Running emergency cleanup..."
    docker system prune -af
  fi
fi
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start

```bash
# Check logs
docker compose logs api --tail=100

# Check container status
docker compose ps -a

# Inspect container
docker inspect api

# Check resource constraints
docker stats --no-stream
```

#### 2. Health Check Failing

```bash
# Test health endpoint manually
curl -v http://localhost:3001/health

# Check from inside container
docker compose exec api wget -qO- http://localhost:3001/health

# Check container networking
docker compose exec api cat /etc/hosts
```

#### 3. Image Pull Failures

```bash
# Verify registry login
docker login ghcr.io

# Check image exists
docker manifest inspect ghcr.io/myorg/api:latest

# Pull with verbose output
docker pull ghcr.io/myorg/api:latest --verbose
```

#### 4. SSH Connection Issues

```bash
# Test Tailscale connection
tailscale ping <ec2-hostname>

# Verify SSH key
ssh -i deploy_key -v user@host

# Check SSH daemon
sudo systemctl status sshd
```

#### 5. Out of Memory

```bash
# Check memory usage
free -h
docker stats --no-stream

# Set memory limits in docker-compose
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
```

#### 6. Port Already in Use

```bash
# Find process using port
sudo lsof -i :3001
sudo netstat -tulpn | grep 3001

# Kill process or change port
docker compose down
# or
# Update port mapping in docker-compose.yml
```

### Debug Commands Reference

```bash
# Container logs
docker compose logs -f api
docker logs api --since 5m

# Container shell
docker compose exec api sh
docker compose exec api /bin/bash

# Process list
docker compose top

# Resource usage
docker stats

# Network inspection
docker network inspect app-network

# Volume inspection
docker volume inspect app_data

# Image layers
docker history ghcr.io/myorg/api:latest

# Build logs
docker compose build --no-cache --progress=plain api
```

### Log Analysis

```bash
# Find errors in logs
docker compose logs api 2>&1 | grep -i error

# Count errors by type
docker compose logs api 2>&1 | grep -i error | sort | uniq -c | sort -rn

# Export logs
docker compose logs api > api-logs-$(date +%Y%m%d).txt
```

---

## Checklist

### Pre-Deployment

- [ ] **Dockerfile**: Multi-stage build optimized
- [ ] **Non-root user**: Container runs as non-root
- [ ] **Health endpoint**: `/health` returns 200 when healthy
- [ ] **.dockerignore**: Excludes unnecessary files
- [ ] **Environment variables**: All secrets documented
- [ ] **Registry access**: GitHub token or credentials configured
- [ ] **EC2 instance**: Docker and Docker Compose installed
- [ ] **Tailscale**: Installed and configured on EC2
- [ ] **SSH key**: Deployment key added to EC2

### GitHub Secrets Required

- [ ] `EC2_HOST` - Tailscale hostname or IP
- [ ] `EC2_USER` - SSH username (e.g., `ubuntu`)
- [ ] `EC2_SSH_KEY` - Private SSH key
- [ ] `TS_OAUTH_CLIENT_ID` - Tailscale OAuth client ID
- [ ] `TS_OAUTH_SECRET` - Tailscale OAuth secret
- [ ] `GITHUB_TOKEN` - Auto-provided, ensure `packages: write`

### EC2 Configuration

- [ ] Security group: Port 22 (SSH) restricted
- [ ] Security group: Application port (3001) as needed
- [ ] Docker installed and running
- [ ] Docker Compose v2 installed
- [ ] App directory created (`~/app`)
- [ ] `.env` file with production variables
- [ ] Tailscale connected to tailnet

### Post-Deployment Verification

- [ ] Containers running: `docker ps`
- [ ] Health check passing: `curl http://localhost:3001/health`
- [ ] Logs clean: `docker compose logs --tail=50`
- [ ] Memory/CPU normal: `docker stats --no-stream`
- [ ] No zombie containers: `docker ps -a`

### Ongoing Maintenance

- [ ] Log rotation configured
- [ ] Disk cleanup cron job
- [ ] Monitoring/alerting setup
- [ ] Backup strategy for volumes
- [ ] Rollback procedure documented
- [ ] Team access documented

---

## Quick Reference

### Essential Commands

```bash
# Deploy
docker compose pull && docker compose up -d

# Logs
docker compose logs -f api

# Status
docker compose ps

# Restart
docker compose restart api

# Rollback
docker compose down && docker compose pull api:previous-tag && docker compose up -d

# Cleanup
docker system prune -af --filter "until=24h"

# Health check
curl -sf http://localhost:3001/health && echo "OK" || echo "FAILED"
```

### Environment Variables Template

```bash
# .env
NODE_ENV=production
PORT=3001

# Database
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DB?schema=public

# Redis
REDIS_URL=redis://localhost:6379

# Auth
BETTER_AUTH_SECRET=your-secret-here
BETTER_AUTH_URL=https://api.example.com

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```
