---
name: performance-expert
description: Optimizes backend, database, and delivery performance — API latency, queries and indexes, N+1, caching, queues, profiling, bundles, CDN. Not for React render issues.
metadata:
  version: "2.2.4"
  tags: "performance, optimization, backend, database, infrastructure"
when_to_use: "slow endpoint, p95 latency, missing index, load testing"
---

# Performance Expert

Backend, database and infrastructure performance. This skill owns the server-side and delivery layer of a stack: request latency, data access, caching, background work, and what ships over the wire.

Render-time work inside React components (re-renders, memoization, virtualized lists, Profiler traces) is a different diagnosis with different tooling. Route it to `react-component-performance` instead of duplicating it here.

## Contract

Inputs:

- A performance symptom with a surface: an endpoint, a query, a job, a build
  output, or a metric that regressed.

Outputs:

- A ranked list of bottlenecks with the measurement that proves each one, plus
  a targeted fix per bottleneck.

Creates/Modifies:

- None on its own. It diagnoses and prescribes; edits happen in the caller's
  workflow.

External Side Effects:

- None. Profiling and load-testing commands are prescribed, not executed
  unattended.

Delegates To:

- `react-component-performance` for React render hotspots, re-render churn,
  memoization, and Profiler-driven component work.
- `workspace-performance-audit` when the target is a whole monorepo rather than
  one surface.

## When to use

- Improving API response times
- Optimizing database queries, indexes and aggregations
- Diagnosing N+1 query patterns
- Implementing caching strategies and invalidation
- Moving heavy work into background jobs or queues
- Profiling a server process or tracing a slow request
- Analyzing shipped bundle size and asset delivery
- Configuring CDN, cache headers or edge caching

## Project context discovery

1. Check the repo's memory/docs (for example `.agents/memory/`, `docs/`) for performance or architecture notes.
2. Identify the performance tools in use (APM, load-testing harness, profiler).
3. Review existing optimizations and caching strategies.
4. Check for a project-specific performance skill.

## Core principles

### Backend

- **API response times:** target < 200ms (p95); use caching, background jobs, connection pooling.
- **Query optimization:** indexes, projections (`select`), pagination, database-side aggregation.
- **Background processing:** queues for heavy operations, async for non-critical tasks, no blocking work in request handlers.

### Database

- **Indexes:** on frequently queried fields, compound indexes, monitor usage.
- **Queries:** filter in `where`, `select` only needed columns, sort with indexes, avoid sequential scans.

### Infrastructure

- **CDN:** edge caching, correct cache headers, static assets off the origin.
- **Serverless:** cold start optimization, memory allocation, provisioned concurrency.

### Delivery layer

- **Bundles:** code splitting by route, dynamic imports for heavy modules, tree shaking, drop unused dependencies.
- **Assets:** WebP images, subset fonts, minify CSS/JS, Gzip/Brotli compression.
- **Server rendering:** static generation for static content, incremental revalidation, framework image and font pipelines.

## Targets

| Area | Metric | Target |
|------|--------|--------|
| Backend | API p50 | < 100ms |
| Backend | API p95 | < 200ms |
| Backend | DB query p95 | < 50ms |
| Backend | Error rate | < 0.1% |
| Delivery | LCP | < 2.5s |
| Delivery | TTFB | < 800ms |
| Delivery | Initial bundle | < 200KB |

## Quick checklist

Backend:

- [ ] Database queries optimized
- [ ] Indexes created and used
- [ ] Caching implemented
- [ ] Background jobs for heavy operations
- [ ] Connection pooling configured

Delivery:

- [ ] Initial bundle < 200KB
- [ ] Code splitting implemented
- [ ] Images optimized and lazy loaded
- [ ] Compression and cache headers configured

## Vet numbers before reporting

Before reporting a measured speedup or regression: name the limiter (what actually bounds the result), confirm every side of the comparison was tuned equally, count errors, and repeat the run.

---

**Database query optimization code, caching strategy implementation, N+1 solutions, background-job patterns, infrastructure tuning, performance testing commands and detailed checklists:** `references/full-guide.md`
