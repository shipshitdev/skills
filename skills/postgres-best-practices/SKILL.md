---
name: postgres-best-practices
description: "Postgres performance optimization and best practices. Covers query performance, connection management, Row-Level Security, schema design, concurrency/locking, monitoring, and advanced features. Use when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations."
license: MIT
metadata:
  version: "1.0.0"
  tags: "postgres, postgresql, sql, performance, rls, indexing, supabase"
  author: "antigravity-awesome-skills"
---

# Postgres Best Practices

Comprehensive performance optimization guide for Postgres. Contains rules across 8 categories, prioritized by impact.

## When to Use

- Writing SQL queries or designing schemas
- Implementing indexes or query optimization
- Reviewing database performance issues
- Configuring connection pooling or scaling
- Working with Row-Level Security (RLS)

## Rule Categories by Priority

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Query Performance | CRITICAL |
| 2 | Connection Management | CRITICAL |
| 3 | Security & RLS | CRITICAL |
| 4 | Schema Design | HIGH |
| 5 | Concurrency & Locking | MEDIUM-HIGH |
| 6 | Data Access Patterns | MEDIUM |
| 7 | Monitoring & Diagnostics | LOW-MEDIUM |
| 8 | Advanced Features | LOW |

## Key Rules

### Query Performance

- **Use indexes for frequently queried columns** — missing indexes are the #1 cause of slow queries
- **Prefer partial indexes** for filtered queries (`WHERE active = true`)
- **Use `EXPLAIN ANALYZE`** to understand query execution plans
- **Avoid `SELECT *`** — select only the columns you need
- **Use `LIMIT`** when you don't need all rows
- **Prefer `EXISTS`** over `COUNT(*)` for existence checks
- **Use CTEs judiciously** — CTEs are optimization fences in older Postgres versions

### Connection Management

- **Use connection poolers** (PgBouncer, Supabase's pooler) for serverless/high-concurrency
- **Set `connection_limit`** in your connection string for serverless environments
- **Use `DIRECT_URL`** for migrations, pooled URL for application queries
- **Close connections properly** — connection leaks exhaust the pool
- **Configure `pool_timeout`** to prevent indefinite waits

### Security & RLS

- **Enable RLS on all tables** that store user data
- **Use `auth.uid()`** in RLS policies (Supabase pattern)
- **Test RLS policies** with different user roles before production
- **Avoid SECURITY DEFINER** functions unless explicitly needed
- **Never store secrets** in database columns without encryption

### Schema Design

- **Use UUIDs or `BIGSERIAL`** for primary keys (avoid int overflow)
- **Add `created_at` and `updated_at`** to all tables
- **Use `NOT NULL` constraints** by default, relax only when necessary
- **Use enums** for fixed value sets instead of arbitrary strings
- **Normalize data** to reduce redundancy, but denormalize for read-heavy paths

### Concurrency & Locking

- **Use `SELECT ... FOR UPDATE`** for read-modify-write cycles
- **Use advisory locks** for application-level distributed locking
- **Keep transactions short** to reduce lock contention
- **Use `ON CONFLICT DO UPDATE`** (upsert) instead of separate SELECT + INSERT

### Monitoring & Diagnostics

```sql
-- Find slow queries
SELECT query, calls, total_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Find missing indexes
SELECT relname, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY seq_scan DESC;

-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();
```

## Index Patterns

```sql
-- Standard index
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Partial index (filtered)
CREATE INDEX CONCURRENTLY idx_posts_published ON posts(created_at)
WHERE published = true;

-- Composite index (column order matters)
CREATE INDEX CONCURRENTLY idx_orders_user_status ON orders(user_id, status);

-- GIN index for JSONB
CREATE INDEX CONCURRENTLY idx_metadata ON items USING GIN (metadata);
```

Always use `CONCURRENTLY` for indexes on production tables to avoid locking.

## Limitations

- Use only when task matches Postgres optimization scope.
- Always test query changes in staging before production.
