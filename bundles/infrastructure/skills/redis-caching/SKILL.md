---
name: redis-caching
description: Implements Redis caching, rate limiting, sessions, locks, and pub/sub for Next.js/NestJS/Prisma apps. Use when adding cache-aside caching or reviewing Redis keys and TTLs.
metadata:
  version: "2.2.5"
  tags: "redis, caching, rate-limiting, sessions, prisma, nestjs, nextjs"
when_to_use: "cache-aside, write-through, rate limiter, TTL, invalidation"
---

# Redis Caching

Implement Redis as a production support layer, not as a second database.

## When to Use

- Add cache-aside or write-through caching around Prisma or API reads.
- Protect expensive routes with rate limiting.
- Store short-lived sessions, verification state, locks, or counters.
- Add pub/sub or stream-backed event fanout.
- Review Redis key design, TTLs, invalidation, or connection handling.

For BullMQ job queue architecture, use `nestjs-queue-architect` instead of duplicating queue patterns here.

## First Decisions

1. Choose the runtime.
   - Long-lived Node.js or NestJS process: use `ioredis`.
   - Serverless or edge runtime: prefer the Upstash Redis SDK or REST API.
   - Background jobs: use BullMQ guidance from `nestjs-queue-architect`.
2. Define the cache contract before coding.
   - Source of truth: Prisma/database, upstream API, computed result, or session authority.
   - Freshness: hard TTL, stale-while-revalidate, explicit invalidation, or write-through.
   - Failure mode: fail open for cache reads, fail closed for auth/session/rate-limit writes.
3. Design keys and invalidation together.
   - Namespace every key: `app:env:entity:id:variant`.
   - Keep keys stable and inspectable.
   - Add TTLs to every cache, lock, session, and rate-limit key.

## Installation

```bash
bun add ioredis

# Optional serverless Redis
bun add @upstash/redis @upstash/ratelimit
```

Use one Redis client per process (a module-level singleton guarded against
hot-reload duplication). Do not create a new TCP client per request. Wire
`error`, `connect`, and `reconnecting` events into the app logger or APM. Avoid
logging credentials from connection URLs.

See `references/examples.md` (§ Redis Client Singleton) for the full setup.

## Cache-Aside With Prisma

Use cache-aside for reads where brief staleness is acceptable: check the
cache, on miss call the loader, write back with a jittered TTL (`baseTtl +
random(0, jitter)`) so hot keys don't all expire in the same instant.

See `references/examples.md` (§ Cache-Aside With Prisma) for the `getCached`
helper and a Prisma-backed usage example.

## Stampede Protection

Protect hot keys with a short `SET key val EX 10 NX` lock. Only the holder
(matched by a random token) releases it; losers wait briefly and re-check the
cache before falling through to a direct load.

See `references/examples.md` (§ Stampede Protection) for the full
lock-and-release implementation.

## Invalidation

Prefer direct invalidation for known keys. Use tag sets (a Redis set per tag,
mapping to the keys written under it) when one mutation affects many keys —
write through a pipeline, invalidate by reading the tag's key set and
`UNLINK`-ing them. Use `SCAN` instead of `KEYS` for emergency pattern cleanup.
Do not put pattern invalidation on hot request paths.

See `references/examples.md` (§ Tag-Based Invalidation) for the
`cacheSetWithTags` / `invalidateTag` implementation.

## Rate Limiting

Use sorted sets for sliding-window limits when exactness matters: trim
expired entries, add the current request, count members, and set the key's
expiry — all in one `MULTI`. For public traffic, set response headers:
`X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After`.

See `references/examples.md` (§ Sliding-Window Rate Limiting) for the full
`slidingWindowRateLimit` implementation.

## Sessions And Verification State

- Store opaque session IDs or token hashes, not raw JWTs or long-lived secrets.
- Set TTL on every session key.
- Regenerate sessions after privilege changes.
- Delete sessions on logout, account deletion, and password reset.
- Treat Redis write failure as auth failure for login, logout, MFA, and password reset flows.

See `references/examples.md` (§ Session Storage) for a `createSession` example.

## Pub/Sub And Streams

- Use pub/sub for ephemeral fanout where missed messages are acceptable.
- Use streams when consumers need replay, backpressure, or durable delivery.
- Keep payloads small; store large objects elsewhere and publish IDs.
- Add consumer observability: lag, dead letters, retries, and handler errors.

## Production Checklist

- [ ] All cache, lock, session, and rate-limit keys have TTLs.
- [ ] Cache reads fail open where possible; auth and rate-limit writes fail closed.
- [ ] Hot keys use TTL jitter or stampede protection.
- [ ] No request path uses `KEYS`, unbounded `SMEMBERS`, or large `HGETALL`.
- [ ] Invalidation is tested alongside the write path.
- [ ] Redis metrics cover latency, hit rate, memory, evictions, blocked clients, and reconnects.
- [ ] Local tests cover cache hit, cache miss, Redis down, invalidation, and rate-limit exceeded.
