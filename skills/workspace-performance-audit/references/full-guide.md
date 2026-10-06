# Workspace Performance Audit - Full Guide

## Orchestration Flow

```
┌─────────────────────────────────────────────────────────────┐
│           WORKSPACE PERFORMANCE AUDIT ORCHESTRATOR          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 0: WORKSPACE DISCOVERY                               │
│  • Identify monorepo structure                              │
│  • Detect apps: web, api, mobile, extension                │
│  • Detect packages: shared, ui, types                      │
│  • Identify tech stack per app                             │
│  • Check for existing metrics/monitoring                   │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  PHASE 1:       │ │  PHASE 2:   │ │  PHASE 3:       │
│  FRONTEND       │ │  BACKEND    │ │  DATABASE       │
│  AUDIT          │ │  AUDIT      │ │  AUDIT          │
└─────────────────┘ └─────────────┘ └─────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: EXTENSION & SHARED PACKAGES AUDIT                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: CONSOLIDATION & PRIORITIZATION                    │
│  • Aggregate findings from all phases                       │
│  • Calculate impact scores                                  │
│  • Prioritize by ROI (impact / effort)                     │
│  • Generate consolidated report                            │
└─────────────────────────────────────────────────────────────┘
```

## Phase Details

### Phase 0: Workspace Discovery

**Goal:** Map the monorepo structure and identify audit targets.

**Actions:**

```bash
# Discover monorepo structure
ls -la apps/
ls -la packages/

# Check package.json for workspace config
cat package.json | grep -A 10 "workspaces"

# Identify tech stacks
cat apps/web/package.json    # Next.js
cat apps/api/package.json    # NestJS
cat apps/extension/package.json  # Plasmo
```

**Output:**

```
Workspace: GenFeedAI
├── apps/
│   ├── web (Next.js 16, React 19)
│   ├── api (NestJS 11, Prisma, Postgres)
│   ├── mobile (Expo 50, React Native)
│   └── extension (Plasmo, Chrome MV3)
├── packages/
│   ├── ui (@genfeedai/ui)
│   ├── shared (@genfeedai/shared)
│   └── types (@genfeedai/types)
```

---

### Phase 1: Frontend Audit (Next.js)

**Skills Invoked:**

- `performance-expert` (primary)
- `design-consistency-auditor`
- `accessibility`

**Metrics to Collect:**

| Metric | Target | Tool |
|--------|--------|------|
| LCP (Largest Contentful Paint) | < 2.5s | Lighthouse |
| FID (First Input Delay) | < 100ms | Lighthouse |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| Initial Bundle Size | < 200KB | webpack-bundle-analyzer |
| Total Bundle Size | < 500KB | webpack-bundle-analyzer |
| Image Optimization | WebP/AVIF | Manual check |
| Code Splitting | Dynamic imports | Manual check |

**Checks:**

```typescript
// Bundle Analysis
// Run: npx @next/bundle-analyzer

// Core Web Vitals
// Run: npx lighthouse https://app.example.com --output=json

// Design Consistency Checks (via design-consistency-auditor)
// - Color palette consistency
// - Typography scale adherence
// - Spacing system compliance
// - Component pattern consistency

// Accessibility Checks (via accessibility skill)
// - WCAG 2.1 AA compliance
// - Keyboard navigation
// - Screen reader compatibility
// - Color contrast ratios (≥ 4.5:1)
```

**Report Template:**

```markdown
## Frontend Performance Report

### Core Web Vitals
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| LCP    | X.Xs    | <2.5s  | ✓/✗    |
| FID    | Xms     | <100ms | ✓/✗    |
| CLS    | X.XX    | <0.1   | ✓/✗    |

### Bundle Analysis
- Initial bundle: XXX KB (target: <200KB)
- Largest chunks: [list]
- Unused code: XX KB

### Design Consistency
- Color violations: X
- Spacing inconsistencies: X
- Component pattern issues: X

### Accessibility
- Critical issues: X
- WCAG violations: [list]

### Recommendations
1. [High Impact] ...
2. [Medium Impact] ...
```

---

### Phase 2: Backend Audit (NestJS)

**Skills Invoked:**

- `performance-expert` (primary)
- `security-expert`

**Metrics to Collect:**

| Metric | Target | Tool |
|--------|--------|------|
| API Response Time (p50) | < 100ms | APM/Logs |
| API Response Time (p95) | < 200ms | APM/Logs |
| Throughput | > 1000 req/s | Load test |
| Error Rate | < 0.1% | Logs |
| Memory Usage | < 512MB | Process metrics |
| CPU Usage | < 70% | Process metrics |

**Checks:**

```typescript
// API Performance Analysis
// - Identify slow endpoints
// - Check N+1 query patterns
// - Validate caching strategy
// - Review connection pooling

// Security Checks (via security-expert)
// - Authentication patterns
// - Rate limiting configuration
// - Input validation
// - CORS configuration
// - Security headers

// Code Quality
// - Async/await patterns
// - Error handling
// - Logging patterns
// - Memory leak potential
```

**Report Template:**

```markdown
## Backend Performance Report

### API Response Times
| Endpoint | p50 | p95 | Target | Status |
|----------|-----|-----|--------|--------|
| GET /api/posts | Xms | Xms | <200ms | ✓/✗ |
| POST /api/posts | Xms | Xms | <200ms | ✓/✗ |

### Resource Usage
- Memory: XXX MB (target: <512MB)
- CPU: XX% (target: <70%)
- Connections: XX active

### Security
- Rate limiting: ✓/✗
- Auth validation: ✓/✗
- Input sanitization: ✓/✗

### N+1 Queries Detected
1. [endpoint]: [query pattern]

### Recommendations
1. [High Impact] ...
2. [Medium Impact] ...
```

---

### Phase 3: Database Audit (Postgres)

**Skills Invoked:**

- `performance-expert` (primary)

**Metrics to Collect:**

| Metric | Target | Tool |
|--------|--------|------|
| Query Time (p95) | < 50ms | `pg_stat_statements` |
| Index Hit Ratio | > 95% | `pg_statio_user_indexes` |
| Connection Pool Usage | < 80% | Connection metrics |
| Slow Queries (>100ms) | 0 | Slow query log |

**Checks:**

```sql
-- Index analysis: unused or rarely used indexes
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC
LIMIT 20;

-- Slow query analysis (requires pg_stat_statements)
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table stats: sequential scans vs index scans
SELECT relname, seq_scan, idx_scan, n_live_tup
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;

-- Connection pool
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Query plan for a suspect query
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

**Report Template:**

```markdown
## Database Performance Report

### Query Performance
| Table | Avg Query Time | Index Usage | Status |
|------------|----------------|-------------|--------|
| posts      | Xms            | XX%         | ✓/✗    |
| users      | Xms            | XX%         | ✓/✗    |

### Index Analysis
- Total indexes: X
- Unused indexes: X
- Missing indexes: [list suggested]

### Slow Queries (>100ms)
1. [query pattern]: Xms
2. [query pattern]: Xms

### Recommendations
1. [High Impact] Add index on...
2. [Medium Impact] Optimize aggregation...
```

---

### Phase 4: Extension & Shared Packages

**Skills Invoked:**

- `performance-expert` (primary)
- `design-consistency-auditor` (for extension UI)

#### Browser Extension Audit

**Metrics:**

| Metric | Target | Tool |
|--------|--------|------|
| Content Script Size | < 50KB | Bundle analysis |
| Background Script Size | < 100KB | Bundle analysis |
| Memory Usage | < 50MB | Chrome DevTools |
| Message Latency | < 10ms | Performance.now() |

**Checks:**

```typescript
// Bundle size
// Check: apps/extension/build/

// Memory profiling
// Chrome DevTools → Memory tab → Heap snapshot

// Message passing performance
// Measure chrome.runtime.sendMessage latency

// Storage efficiency
// Check chrome.storage.local usage
```

#### Shared Packages Audit

**Checks:**

```bash
# Dependency duplication
npx depcheck

# Bundle contribution analysis
# Check how much each package adds to final bundles

# Tree-shaking effectiveness
# Verify unused exports are eliminated

# Version consistency
# Check for version mismatches across apps
```

**Report Template:**

```markdown
## Extension & Packages Report

### Browser Extension
- Content script: XX KB (target: <50KB)
- Background script: XX KB (target: <100KB)
- Memory usage: XX MB (target: <50MB)

### Shared Packages
| Package | Size | Used By | Tree-Shakeable |
|---------|------|---------|----------------|
| @org/ui | XX KB | web, extension | ✓/✗ |
| @org/shared | XX KB | all | ✓/✗ |

### Dependency Issues
- Duplicates: [list]
- Version conflicts: [list]
- Unused: [list]

### Recommendations
1. [High Impact] ...
```

---

### Phase 5: Consolidation & Prioritization

**Skills Invoked:**

- `qa-reviewer` (validation)

**Actions:**

1. Aggregate all findings from Phases 1-4
2. Calculate impact scores (1-10)
3. Estimate effort (hours/days)
4. Calculate ROI = Impact / Effort
5. Prioritize recommendations

**Final Report Template:**

```markdown
# Workspace Performance Audit Report
**Project:** [Name]
**Date:** YYYY-MM-DD
**Auditor:** Claude

## Executive Summary
- Overall Health Score: X/10
- Critical Issues: X
- High Priority Items: X
- Quick Wins Identified: X

## Health by Domain
| Domain | Score | Critical | High | Medium | Low |
|--------|-------|----------|------|--------|-----|
| Frontend | X/10 | X | X | X | X |
| Backend | X/10 | X | X | X | X |
| Database | X/10 | X | X | X | X |
| Extension | X/10 | X | X | X | X |
| Packages | X/10 | X | X | X | X |

## Prioritized Recommendations

### Quick Wins (High Impact, Low Effort)
1. **[Domain]** Issue description
   - Impact: X/10
   - Effort: X hours
   - Action: ...

### High Priority (High Impact, Medium Effort)
1. **[Domain]** Issue description
   - Impact: X/10
   - Effort: X days
   - Action: ...

### Technical Debt (Medium Impact, Variable Effort)
1. **[Domain]** Issue description
   - Impact: X/10
   - Effort: X days
   - Action: ...

## Next Steps
1. Address critical issues immediately
2. Schedule quick wins for next sprint
3. Add high priority items to backlog
4. Review technical debt quarterly
```

## Best Practices

### Before Audit

- Ensure all apps are buildable
- Have access to production metrics if available
- Clear any local caches for accurate bundle analysis

### During Audit

- Document current state before changes
- Take screenshots of metrics
- Note any anomalies or edge cases

### After Audit

- Create tickets for each recommendation
- Establish baseline metrics
- Schedule follow-up audit (quarterly recommended)

## Example Interaction

**User:** "Run a performance audit on the GenFeedAI monorepo"

**Orchestrator:**

```
Starting Workspace Performance Audit...

Phase 0: Workspace Discovery
✓ Found monorepo structure
✓ Detected apps: web, api, extension
✓ Detected packages: ui, shared, types

Phase 1: Frontend Audit (apps/web)
✓ Core Web Vitals collected
✓ Bundle analysis complete
✓ Design consistency checked
✓ Accessibility validated

Phase 2: Backend Audit (apps/api)
✓ API response times measured
✓ N+1 queries detected: 3
✓ Security configuration reviewed

Phase 3: Database Audit
✓ Query performance analyzed
✓ Index usage reviewed
✓ Slow queries identified: 2

Phase 4: Extension & Packages
✓ Extension bundle analyzed
✓ Shared package sizes measured
✓ Dependency audit complete

Phase 5: Consolidation
✓ Findings aggregated
✓ Recommendations prioritized

═══════════════════════════════════════
AUDIT COMPLETE

Overall Health: 7.2/10

Top 3 Quick Wins:
1. Add index on posts.userId (Database) - 2x query improvement
2. Enable Next.js image optimization (Frontend) - 40% LCP improvement
3. Implement response caching (Backend) - 50% latency reduction

Critical Issues: 1
- N+1 query in /api/feed endpoint

Full report generated at: .agents/memory/performance-audit-2025-01-XX.md
═══════════════════════════════════════
```
