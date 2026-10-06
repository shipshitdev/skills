# Performance Expert - Full Guide

Backend, database, and infrastructure performance. For React render hotspots,
re-render churn, memoization, and Profiler-driven component work, use the
`react-component-performance` skill instead.

## Core Performance Principles

### 1. Backend Performance

**API Response Times:**

- Target: < 200ms (p95)
- Database queries optimized
- Caching implemented
- Background jobs for heavy operations
- Connection pooling configured

**Query Optimization:**

- Indexes on frequently queried fields
- Compound indexes for multi-field queries
- Projections to limit fields
- Pagination implemented
- Aggregation pipelines optimized

**Caching Strategy:**

- Cache frequently accessed data (e.g. Redis)
- Cache invalidation strategy
- Cache TTL configured
- Cache warming for critical data

**Background Processing:**

- Heavy operations in queues (e.g. BullMQ)
- Async processing for non-critical tasks
- WebSocket for real-time updates
- No blocking operations in request handlers

### 2. Database Performance

**Index Strategy:**

- Indexes on frequently queried fields
- Compound indexes for multi-field queries
- Indexes on foreign keys
- No unnecessary indexes
- Index usage monitored

**Query Optimization:**

- Filter in the `where` clause, not in application code
- `select` only the columns needed
- `take`/`skip` or cursor pagination
- Sort with indexes
- Avoid sequential scans on large tables (check `EXPLAIN (ANALYZE, BUFFERS)`)

**Relations and Aggregation:**

- `include`/`select` relations in one query instead of looping
- Aggregate in the database (`groupBy`, `_count`, `_sum`) rather than in memory
- Index usage verified in the query plan
- Use `$queryRaw` (tagged template) for hand-tuned SQL
- Batch lookups with `where: { id: { in: ids } }`

**Connection Management:**

- Connection pooling configured
- Connection limits set
- Idle connections closed
- Connection monitoring

### 3. Infrastructure Performance

**CDN Configuration:**

- Edge caching configured
- Cache headers set correctly
- Static assets on CDN
- Edge locations optimized
- Cache invalidation strategy

**Serverless Optimization:**

- Cold start optimization
- Memory allocation optimized
- Connection pooling
- Provisioned concurrency (if needed)
- Function size minimized

**Managed Database:**

- Performance tier appropriate for load
- Read replicas configured (if needed)
- Connection pooling optimized
- Monitoring enabled
- Query performance tracked

### 4. Delivery Layer

**Bundle Optimization:**

- Code splitting by route
- Dynamic imports for heavy modules
- Tree shaking enabled
- Remove unused dependencies
- Optimize large dependencies

**Server Rendering:**

- Static generation for static content
- Incremental revalidation for semi-static content
- Framework image pipeline for responsive images
- Font and script loading optimized

**Asset Optimization:**

- Images optimized (WebP, compression)
- Fonts subset and preloaded
- CSS minified and purged
- JavaScript minified
- Gzip/Brotli compression

## Performance Metrics

### Backend Metrics

- **API Response Time (p50)**: < 100ms
- **API Response Time (p95)**: < 200ms
- **API Response Time (p99)**: < 500ms
- **Database Query Time**: < 50ms (p95)
- **Error Rate**: < 0.1%
- **Throughput**: Monitor requests/second

### Database Metrics

- **Query Execution Time**: < 50ms (p95)
- **Index Hit Ratio**: > 95%
- **Connection Pool Usage**: < 80%
- **Slow Query Count**: < 1% of queries

### Delivery Metrics

- **TTFB (Time to First Byte)**: < 800ms
- **LCP (Largest Contentful Paint)**: < 2.5s
- **Initial bundle**: < 200KB
- **Cache hit ratio at the edge**: > 90%

## Common Performance Issues

### 1. N+1 Queries

**Problem:** Multiple database queries in loops

**Solution:**

```typescript
// BAD: N+1 queries
async findAll() {
  const users = await this.prisma.user.findMany();
  for (const user of users) {
    user.posts = await this.prisma.post.findMany({ where: { userId: user.id } });
  }
  return users;
}

// GOOD: one query with the relation included
async findAll() {
  return this.prisma.user.findMany({
    include: { posts: true },
  });
}
```

### 2. Large Bundle Size

**Problem:** JavaScript bundle too large

**Solution:**

- Code splitting by route
- Dynamic imports for heavy modules
- Remove unused dependencies
- Optimize large libraries
- Tree shaking enabled

### 3. Missing Indexes

**Problem:** Slow database queries

**Solution:**

```prisma
// Declare indexes in the model, then ship them as a migration
model User {
  id    String @id @default(cuid())
  email String @unique
}

model Post {
  id             String   @id @default(cuid())
  organizationId String
  createdAt      DateTime @default(now())

  @@index([organizationId, createdAt(sort: Desc)])
}
```

### 4. Blocking Operations

**Problem:** Heavy operations blocking request handlers

**Solution:**

- Move to background jobs
- Use queues (e.g. BullMQ)
- Async processing
- WebSocket for real-time updates

### 5. Cache Stampede

**Problem:** A hot key expires and every request rebuilds it at once

**Solution:**

- Stagger TTLs so keys expire at different times
- Serve stale while a single request revalidates
- Lock or single-flight the rebuild
- Warm critical keys before traffic arrives

## Performance Optimization Patterns

### Database Query Optimization

```typescript
// Projection
const users = await this.userModel.find(
  { organization },
  { email: 1, name: 1 } // Only needed fields
);

// Pagination
const posts = await this.postModel.find({})
  .limit(20)
  .skip(page * 20)
  .sort({ createdAt: -1 });

// Indexed query
const users = await this.userModel.find({
  organization: orgId,  // Indexed field
  isDeleted: false
});
```

### Caching Strategy

```typescript
// Redis caching
async findAll(organizationId: string) {
  const cacheKey = `users:${organizationId}`;
  const cached = await this.redis.get(cacheKey);

  if (cached) {
    return JSON.parse(cached);
  }

  const users = await this.userModel.find({ organization: organizationId });
  await this.redis.setex(cacheKey, 3600, JSON.stringify(users));

  return users;
}
```

### Background Jobs

```typescript
// Return fast; do the expensive work off the request path
async requestExport(organizationId: string) {
  await this.exportQueue.add('generate', { organizationId });
  return { status: 'queued' };
}
```

### Delivery Layer

```typescript
// Static generation with incremental revalidation
export async function getStaticProps() {
  return {
    props: { data },
    revalidate: 3600
  };
}

// Dynamic import for a heavy module kept off the initial bundle
const HeavyModule = dynamic(() => import('./HeavyModule'), { ssr: false });
```

## Performance Testing

**Load Testing:**

```bash
# Using k6
k6 run load-test.js

# Test scenarios:
# - Normal load
# - Peak load
# - Stress test
# - Spike test
```

**Profiling:**

```bash
# Node.js profiling
node --prof app.js
node --prof-process isolate-*.log
```

**Bundle Analysis:**

```bash
# Analyze bundle
bun run build
bun run analyze

# Or with a bundle analyzer plugin
ANALYZE=true bun run build
```

## Performance Checklist

### Backend

- [ ] Database queries optimized
- [ ] Indexes created and used
- [ ] Caching implemented
- [ ] Background jobs for heavy operations
- [ ] Connection pooling configured
- [ ] Response compression enabled
- [ ] Rate limiting configured
- [ ] Monitoring enabled

### Database

- [ ] Indexes on frequently queried fields
- [ ] Compound indexes for multi-field queries
- [ ] Query projections used
- [ ] Pagination implemented
- [ ] Aggregation pipelines optimized
- [ ] Connection pooling configured
- [ ] Read replicas configured (if needed)

### Infrastructure

- [ ] CDN configured
- [ ] Caching strategy implemented
- [ ] Auto-scaling configured
- [ ] Monitoring and alerting set up
- [ ] Cost optimization reviewed

### Delivery

- [ ] Bundle size optimized (< 200KB initial)
- [ ] Code splitting implemented
- [ ] Images optimized and lazy loaded
- [ ] Fonts optimized
- [ ] CSS purged
- [ ] JavaScript minified
- [ ] Gzip/Brotli compression enabled
- [ ] Caching headers configured

## Best Practices

1. **Measure First:** Profile before optimizing
2. **Set Targets:** Define performance budgets
3. **Monitor Continuously:** Track metrics over time
4. **Optimize Incrementally:** Make small, measurable changes
5. **Test Regularly:** Load test before deployment
6. **Cache Strategically:** Cache what makes sense
7. **Index Thoughtfully:** Indexes improve reads but slow writes
8. **Monitor Costs:** Balance performance and cost
