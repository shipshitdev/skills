---
name: prisma-expert
description: "Expert in Prisma ORM: schema design, migrations, query optimization, N+1 prevention, connection management, and transaction patterns across PostgreSQL, MySQL, and SQLite. Use when designing Prisma schemas, debugging migrations, or optimizing database queries."
license: MIT
metadata:
  version: "1.0.0"
  tags: "prisma, orm, typescript, postgresql, migrations, query-optimization"
  author: "antigravity-awesome-skills"
---

# Prisma Expert

Expert in Prisma ORM with deep knowledge of schema design, migrations, query optimization, relations modeling, and database operations across PostgreSQL, MySQL, and SQLite.

## When to Use

- Setting up or modifying Prisma schemas
- Writing complex relational queries
- Debugging migration issues or schema drift
- Optimizing database performance (N+1, connection pooling)
- Implementing transaction patterns
- Migrating from other ORMs to Prisma

## Do Not Use

- Raw SQL optimization → use `postgres-best-practices`
- Database server configuration → DevOps skill
- Connection pooling at infrastructure level → `neon-postgres` or similar

## Schema Design

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  posts     Post[]   @relation("UserPosts")
  profile   Profile? @relation("UserProfile")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
  @@map("users")
}

model Post {
  id       String @id @default(cuid())
  title    String
  author   User   @relation("UserPosts", fields: [authorId], references: [id], onDelete: Cascade)
  authorId String

  @@index([authorId])
  @@map("posts")
}
```

## Migration Workflow

```bash
# Development
npx prisma migrate dev --name descriptive_name

# Production (NEVER use migrate dev)
npx prisma migrate deploy

# If migration fails in production
npx prisma migrate resolve --applied "migration_name"
# or
npx prisma migrate resolve --rolled-back "migration_name"

# Validate schema
npx prisma validate

# Format schema
npx prisma format
```

## Query Optimization

```typescript
// BAD: N+1 problem
const users = await prisma.user.findMany()
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } })
}

// GOOD: Include relations
const users = await prisma.user.findMany({
  include: { posts: true },
})

// BETTER: Select only needed fields
const users = await prisma.user.findMany({
  select: {
    id: true,
    email: true,
    posts: { select: { id: true, title: true } },
  },
})

// BEST for complex aggregations: raw query
const result = await prisma.$queryRaw`
  SELECT u.id, COUNT(p.id) as post_count
  FROM users u LEFT JOIN posts p ON p.author_id = u.id
  GROUP BY u.id
`
```

## Connection Management (Serverless)

```typescript
// Singleton pattern for serverless (Next.js, Vercel)
const globalForPrisma = global as unknown as { prisma: PrismaClient }

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query'] : [],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

process.on('beforeExit', async () => {
  await prisma.$disconnect()
})
```

```env
# With pool settings in DATABASE_URL
DATABASE_URL="postgresql://user:pass@host:5432/db?connection_limit=5&pool_timeout=10"
```

## Transaction Patterns

```typescript
// Sequential operations
const [user, profile] = await prisma.$transaction([
  prisma.user.create({ data: userData }),
  prisma.profile.create({ data: profileData }),
])

// Interactive transaction with validation
const result = await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({ data: userData })
  if (user.email.endsWith('@blocked.com')) throw new Error('Blocked domain')
  return tx.profile.create({ data: { ...profileData, userId: user.id } })
}, {
  maxWait: 5000,
  timeout: 10000,
  isolationLevel: 'Serializable',
})
```

## Code Review Checklist

- [ ] All models have appropriate `@id` and primary keys
- [ ] Relations use explicit `@relation` with `fields` and `references`
- [ ] Cascade behaviors defined (`onDelete`, `onUpdate`)
- [ ] Indexes on frequently queried `WHERE` clause fields
- [ ] `select` used to fetch only required fields
- [ ] No N+1 queries (use includes or relational queries)
- [ ] `migrate dev` never used in production
- [ ] Connection pooling configured for serverless

## Anti-Patterns

1. **`additionalProperties: true`** in strict schemas
2. **Using `migrate dev`** in production (data loss risk)
3. **No `select`** on large models (over-fetching)
4. **Ignoring connection limits** in serverless environments
5. **Nested transactions** without understanding Prisma's transaction model

## Limitations

- Use only when task matches Prisma ORM scope.
- Always test migrations in staging before production deployment.
