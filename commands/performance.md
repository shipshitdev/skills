# Performance - Performance Analysis Command

Analyze and optimize performance across frontend, backend, database, and infrastructure.

## When to Use

- Performance issues reported
- Slow page loads or API responses
- Database query optimization needed
- Before scaling
- Bundle size concerns

## Context Discovery

Before analyzing, discover the project's actual stack:

1. Check `package.json` for framework (React, Next.js, Electron, etc.)
2. Identify database (PostgreSQL/RDS, SQLite, etc.)
3. Check for build tools (Vite, Turbopack, Bun, etc.)
4. Look for existing monitoring (Sentry, Datadog, etc.)

**Adapt all analysis to the discovered stack. Do not assume any specific framework.**

## Frontend Performance

### Bundle Analysis

```bash
bun run build
# Check output sizes in build log
```

Check for: code splitting, tree shaking, unused dependencies, large imports.

### Core Web Vitals (web apps)

- **LCP** < 2.5s, **FID** < 100ms, **CLS** < 0.1

### React Performance

- Memoization (`useMemo`, `useCallback`) where needed
- Virtualization for long lists
- Lazy loading routes/components
- Image optimization

### Electron Performance (desktop apps)

- IPC message size and frequency
- Main process blocking
- Memory leaks (renderer not GC'd)
- Startup time (preload scripts, lazy window creation)
- SQLite query performance (better-sqlite3 is sync — keep queries fast)

## Backend / API Performance

- Response times < 200ms (p95)
- Connection pooling configured
- Caching where appropriate
- Heavy work offloaded to background jobs
- N+1 query detection

## Database Performance

### PostgreSQL / AWS RDS

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Check index usage
SELECT relname, idx_scan, seq_scan
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
```

Check for: missing indexes, N+1 queries, unoptimized joins, missing pagination, connection pool sizing.

### SQLite (Electron apps)

- Queries should be < 10ms for UI responsiveness
- Use WAL mode for concurrent reads
- Index frequently filtered columns
- Batch writes in transactions

## Infrastructure

### Vercel (web apps)

- Edge functions for latency-sensitive routes
- ISR / static generation where possible
- Image optimization via Vercel

### AWS RDS

- Instance sizing appropriate for load
- Read replicas if needed
- Connection pooling (PgBouncer or RDS Proxy)
- Automated backups and monitoring

## Output Format

```
PERFORMANCE ANALYSIS

Project: [name]
Stack: [discovered stack]

METRICS
[measured values vs targets]

ISSUES FOUND
1. [Issue] — Impact: [what], Fix: [how], Priority: HIGH/MED/LOW

RECOMMENDATIONS
[prioritized action items]
```

## Checklist

- [ ] Discover actual project stack
- [ ] Measure current metrics
- [ ] Identify bottlenecks
- [ ] Provide specific fixes with code examples
- [ ] Prioritize by impact
