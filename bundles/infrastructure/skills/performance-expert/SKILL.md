---
name: performance-expert
description: Optimizes backend, database, and delivery performance — API latency, queries and indexes, N+1, caching, queues, profiling, bundles, CDN. Not for React render issues.
metadata:
  version: "2.2.3"
  tags: "performance, optimization, backend, database, infrastructure"
when_to_use: "slow endpoint, p95 latency, missing index, load testing"
---

# Performance Expert Skill

Backend, database, and infrastructure performance. This skill owns the
server-side and delivery-layer of a stack: request latency, data access,
caching, background work, and what ships over the wire.

Render-time work inside React components — re-renders, memoization,
virtualized lists, Profiler traces — is a different diagnosis with different
tooling. Route it to `react-component-performance` instead of duplicating it
here.

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

## When to Use

- Improving API response times
- Optimizing database queries, indexes, and aggregations
- Diagnosing N+1 query patterns
- Implementing caching strategies and invalidation
- Moving heavy work into background jobs or queues
- Profiling a server process or tracing a slow request
- Analyzing shipped bundle size and asset delivery
- Configuring CDN, cache headers, or edge caching

## Project Context Discovery

1. Check `.agents/memory/` for performance architecture context (e.g., any
   `*performance*` or `*architecture*` files)
2. Identify performance tools (APM, load-testing harness, profiler)
3. Review existing optimizations and caching strategies
4. Check for `[project]-performance-expert` skill

## Core Performance Principles

### Backend

**API Response Times:** Target < 200ms (p95), caching, background jobs, connection pooling

**Query Optimization:** Indexes, projections (`select`), pagination, database-side aggregation

**Background Processing:** Queues for heavy operations, async for non-critical tasks, no blocking work in request handlers

### Database

**Indexes:** On frequently queried fields, compound indexes, monitor usage

**Queries:** Filter in `where`, `select` only needed columns, sort with indexes, avoid sequential scans

### Infrastructure

**CDN:** Edge caching, correct cache headers, static assets off the origin

**Serverless:** Cold start optimization, memory allocation, provisioned concurrency

### Delivery Layer

**Bundles:** Code splitting by route, dynamic imports for heavy modules, tree shaking, drop unused dependencies

**Assets:** WebP images, subset fonts, minify CSS/JS, Gzip/Brotli compression

**Server rendering:** Static generation for static content, incremental revalidation, framework image and font pipelines

## Performance Metrics

### Backend

- **API p50:** < 100ms
- **API p95:** < 200ms
- **DB Query p95:** < 50ms
- **Error Rate:** < 0.1%

### Delivery

- **LCP:** < 2.5s
- **TTFB:** < 800ms
- **Initial bundle:** < 200KB

## Quick Checklist

### Backend

- [ ] Database queries optimized
- [ ] Indexes created and used
- [ ] Caching implemented
- [ ] Background jobs for heavy operations
- [ ] Connection pooling configured

### Delivery

- [ ] Bundle size < 200KB initial
- [ ] Code splitting implemented
- [ ] Images optimized and lazy loaded
- [ ] Compression and cache headers configured

Before reporting a measured speedup or regression, vet the number with the `pstack` skill's benchmark checklist reference: name the limiter, confirm every side was tuned, count errors, and repeat the run.

---

**For database query optimization code, caching strategy implementation, N+1 query solutions, background-job patterns, infrastructure tuning, performance testing commands, and detailed checklists, see:** `references/full-guide.md`
