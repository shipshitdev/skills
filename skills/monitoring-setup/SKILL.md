---
name: monitoring-setup
description: "Sets up production monitoring for NestJS and Next.js: Sentry, Google Analytics, and alerts on BullMQ queue depth and Postgres slow queries or connection saturation."
metadata:
  version: "2.2.2"
  tags: "monitoring, sentry, analytics, observability, alerting, bullmq, postgres"
when_to_use: "error tracking, observability, alerting"
---

# Monitoring Setup

Two layers: **application** health (errors, user behavior) and **operational** health
(are the queues draining, is the database keeping up). An app with clean Sentry but a
queue backing up or a table scan on every request is still failing its users — cover
both.

## When to Use

- Need to set up error tracking (Sentry)
- Want to configure Google Analytics
- Need monitoring for production applications
- Want to track application errors and user behavior
- Need operational signals: queue depth, slow queries, connection saturation, and
  alerts on them

## Sentry Setup

### NestJS Backend

1. Install: `bun add @sentry/node @sentry/profiling-node`
2. Initialize in `main.ts` before app creation
3. Configure DSN via `SENTRY_DSN` environment variable
4. Set appropriate sample rates for production

### Next.js Frontend

1. Install: `bun add @sentry/nextjs`
2. Run: `bunx @sentry/wizard@latest -i nextjs`
3. Configure client/server/edge configs
4. Set `NEXT_PUBLIC_SENTRY_DSN` for client-side

## Google Analytics Setup

### Next.js Setup

1. Add Google Analytics script to root layout
2. Use `NEXT_PUBLIC_GA_MEASUREMENT_ID` (format: G-XXXXXXXXXX)
3. Create analytics utility functions for event tracking
4. Set up page view tracking

### Common Events

- User signup/login
- Purchases/conversions
- Feature usage
- Custom business events

## Operational Monitoring

Application errors tell you what threw; operational signals tell you what is quietly
degrading. Instrument the three that take a product down under load.

### BullMQ queue depth

A queue that fills faster than it drains is an outage in slow motion — no error fires
until jobs time out.

- Track per queue: **waiting** (backlog), **active**, **failed**, and **completed
  rate**. `Queue.getJobCounts()` exposes these; scrape them on an interval or via
  `bullmq-prometheus`.
- The signal that matters is **trend**: waiting climbing while completed is flat means
  workers cannot keep up (scale workers or the Redis connection).
- Watch the **dead-letter / failed** set — jobs exhausting retries are silent data loss.

### Postgres slow queries & connections

- Enable `pg_stat_statements`; surface the top queries by total time and by mean time.
  A query that is individually fast but runs 10k×/min is the real cost.
- Log queries over a threshold (`log_min_duration_statement`) and alert on new
  entrants — a slow query usually means a missing index or an N+1.
- Track **connection saturation** (`active / max_connections`). Near the ceiling on
  serverless means the pooler is undersized — see `postgres-ops`.

### Redis

- Memory usage vs `maxmemory`, eviction rate, and command latency. Evictions mean the
  cache is too small and hit-rate is silently dropping.

## Alerting

Instrumentation no one looks at is not monitoring. For each signal above, define a
threshold and route it somewhere a human sees at 3am (PagerDuty, Opsgenie, a Slack
channel that pages). Alert on the **leading** indicator (queue waiting climbing,
connections near max) not just the **lagging** one (jobs already timing out, 500s
already served). Every alert names the runbook step to take, or it is just noise.

## Best Practices

- Use different DSNs for dev/prod
- Set appropriate sample rates
- Respect user privacy (GDPR/CCPA)
- Don't track sensitive data
- Alert on leading operational indicators, not only on errors after the fact
- Every alert links to a runbook action — no orphan alerts

## Integration

This skill integrates with `/monitoring-setup` command for automated setup workflows.
Pairs with `postgres-ops` (pooling, DR) and `nestjs-queue-architect` (queue design).
