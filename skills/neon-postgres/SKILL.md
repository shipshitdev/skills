---
name: neon-postgres
description: "Expert patterns for Neon serverless Postgres: branching, connection pooling, Prisma/Drizzle integration, serverless HTTP driver, and database branching workflows. Use when working with Neon as your Postgres provider."
license: MIT
metadata:
  version: "1.0.0"
  tags: "neon, postgres, serverless, prisma, drizzle, connection-pooling"
  author: "antigravity-awesome-skills"
---

# Neon Postgres

Expert patterns for Neon serverless Postgres, including branching, connection pooling, and ORM integration.

## When to Use

- Setting up Neon as your Postgres provider
- Configuring connection pooling for serverless environments
- Integrating Neon with Prisma, Drizzle, or raw SQL
- Using Neon's database branching for preview environments
- Optimizing connections for Vercel, AWS Lambda, or Cloudflare Workers

## Core Concepts

### Two Connection Strings

Neon requires two connection strings:

| Variable | Use | Driver |
|----------|-----|--------|
| `DATABASE_URL` | Application queries (pooled) | PgBouncer |
| `DIRECT_URL` | Migrations/DDL operations | Direct |

Migrations fail through PgBouncer. Always set `directUrl` in Prisma schema.

### Prisma + Neon Setup

```env
# .env
DATABASE_URL="postgres://user:pass@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
DIRECT_URL="postgres://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}
```

```typescript
// lib/prisma.ts — singleton for serverless
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient | undefined }

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
})

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

### Drizzle + Neon Serverless Driver

```typescript
// db/index.ts
import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'
import * as schema from './schema'

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql, { schema })
```

Use `neon-http` for single queries (fastest for serverless).
Use `neon-serverless` (WebSocket) when you need transactions.

### Database Branching

Neon supports Git-like database branches for preview environments:

```bash
# Install Neon CLI
npm install -g neonctl

# Create a branch for a PR
neonctl branches create --name preview/pr-123

# Get connection string for branch
neonctl connection-string --branch preview/pr-123
```

Branch from `main` (production) to get a copy of all data. Merge or delete when PR closes.

### Connection Pooling for Serverless

```
# Maximum connections without pooler: ~100
# With PgBouncer pooler: up to 10,000 connections
# 
# Serverless function invocations can spike — always use the -pooler endpoint
```

## Anti-Patterns

| Wrong | Why | Fix |
|-------|-----|-----|
| Pooled URL for migrations | DDL fails through PgBouncer | Set `directUrl` in schema |
| No connection pooling | Exhausts connection limits at scale | Use `-pooler` endpoint |
| New client per request | Connection churn and latency | Use singleton/global client |

## Full Reference

See `references/full-guide.md` for complete Drizzle patterns, Next.js integration, edge runtime setup, and advanced branching workflows.

## Limitations

- Use only when task matches Neon Postgres scope.
- Verify connection limits and pricing in Neon dashboard before scaling.
