---
name: redis-caching
description: Implement Redis caching, session storage, rate limiting, pub/sub, and job queues in Node.js, Next.js, and NestJS applications using ioredis and BullMQ
---

# Redis Caching

Expert in Redis integration patterns for production Node.js applications — caching, sessions, rate limiting, pub/sub, and background jobs.

## When to Use This Skill

Use when you're:

- Adding caching to API routes or database queries
- Implementing session storage with Redis
- Building rate limiters for APIs
- Setting up pub/sub for real-time features
- Adding background job queues with BullMQ
- Configuring Redis for Next.js or NestJS
- Optimizing performance with cache-aside, write-through, or write-behind patterns

## Quick Setup

```bash
# Core Redis client
npm install ioredis

# For job queues
npm install bullmq

# For NestJS
npm install @nestjs/bullmq bullmq ioredis
```

```env
REDIS_URL=redis://localhost:6379
# Or with auth:
REDIS_URL=redis://:password@host:6379/0
```

## Connection Setup

### Basic ioredis Connection

```typescript
import Redis from 'ioredis';

// Single instance (recommended for most apps)
const redis = new Redis(process.env.REDIS_URL, {
  maxRetriesPerRequest: 3,
  retryStrategy(times) {
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
  lazyConnect: true, // Don't connect until first command
});

// Cluster mode (for production at scale)
const cluster = new Redis.Cluster([
  { host: 'node1', port: 6379 },
  { host: 'node2', port: 6379 },
], {
  redisOptions: { password: process.env.REDIS_PASSWORD },
  scaleReads: 'slave',
});
```

### NestJS Module Setup

```typescript
import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';

@Module({
  imports: [
    BullModule.forRoot({
      connection: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
      },
    }),
    BullModule.registerQueue({ name: 'email' }),
    BullModule.registerQueue({ name: 'notifications' }),
  ],
})
export class AppModule {}
```

## Caching Patterns

### Cache-Aside (Lazy Loading)

The most common pattern. Check cache first, fetch from source on miss, populate cache.

```typescript
async function getCached<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlSeconds = 300,
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const data = await fetcher();
  await redis.setex(key, ttlSeconds, JSON.stringify(data));
  return data;
}

// Usage
const user = await getCached(
  `user:${id}`,
  () => db.user.findUnique({ where: { id } }),
  600, // 10 minutes
);
```

### Write-Through Cache

Update cache when writing to the database. Keeps cache fresh but adds write latency.

```typescript
async function updateUser(id: string, data: UpdateUserDto) {
  const user = await db.user.update({ where: { id }, data });
  await redis.setex(`user:${id}`, 600, JSON.stringify(user));
  return user;
}
```

### Cache Invalidation

```typescript
// Single key
await redis.del(`user:${id}`);

// Pattern-based (use sparingly — SCAN is O(N))
async function invalidatePattern(pattern: string) {
  let cursor = '0';
  do {
    const [nextCursor, keys] = await redis.scan(
      cursor, 'MATCH', pattern, 'COUNT', 100,
    );
    cursor = nextCursor;
    if (keys.length) await redis.del(...keys);
  } while (cursor !== '0');
}

// Invalidate all user-related cache
await invalidatePattern('user:*');
```

### Cache Stampede Prevention

When a popular key expires, many requests hit the DB simultaneously.

```typescript
async function getCachedWithLock<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlSeconds = 300,
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  const acquired = await redis.set(lockKey, '1', 'EX', 10, 'NX');

  if (acquired) {
    try {
      const data = await fetcher();
      await redis.setex(key, ttlSeconds, JSON.stringify(data));
      return data;
    } finally {
      await redis.del(lockKey);
    }
  }

  // Another process is fetching — wait and retry
  await new Promise((r) => setTimeout(r, 100));
  return getCachedWithLock(key, fetcher, ttlSeconds);
}
```

## Rate Limiting

### Sliding Window Rate Limiter

```typescript
async function rateLimit(
  identifier: string,
  limit: number,
  windowSeconds: number,
): Promise<{ allowed: boolean; remaining: number; resetIn: number }> {
  const key = `ratelimit:${identifier}`;
  const now = Date.now();
  const windowStart = now - windowSeconds * 1000;

  const multi = redis.multi();
  multi.zremrangebyscore(key, 0, windowStart); // Remove old entries
  multi.zadd(key, now, `${now}`);              // Add current request
  multi.zcard(key);                            // Count requests in window
  multi.expire(key, windowSeconds);            // Set TTL

  const results = await multi.exec();
  const count = results![2][1] as number;

  return {
    allowed: count <= limit,
    remaining: Math.max(0, limit - count),
    resetIn: windowSeconds,
  };
}

// Express/Next.js middleware
async function rateLimitMiddleware(req, res, next) {
  const ip = req.ip || req.headers['x-forwarded-for'];
  const { allowed, remaining, resetIn } = await rateLimit(ip, 100, 60);

  res.setHeader('X-RateLimit-Remaining', remaining);
  res.setHeader('X-RateLimit-Reset', resetIn);

  if (!allowed) {
    return res.status(429).json({ error: 'Too many requests' });
  }
  next();
}
```

## Session Storage

### Express/Next.js Sessions with Redis

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';

const store = new RedisStore({
  client: redis,
  prefix: 'sess:',
  ttl: 86400, // 24 hours
});

app.use(session({
  store,
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 86400000,
  },
}));
```

## Pub/Sub

### Real-Time Event Broadcasting

```typescript
// Publisher (use a separate connection for pub/sub)
const publisher = new Redis(process.env.REDIS_URL);

async function publishEvent(channel: string, data: unknown) {
  await publisher.publish(channel, JSON.stringify(data));
}

// Subscriber (dedicated connection — cannot be shared)
const subscriber = new Redis(process.env.REDIS_URL);

subscriber.subscribe('notifications', 'chat');
subscriber.on('message', (channel, message) => {
  const data = JSON.parse(message);
  console.log(`[${channel}]`, data);
});
```

## Job Queues with BullMQ

### Producer

```typescript
import { Queue } from 'bullmq';

const emailQueue = new Queue('email', {
  connection: { host: 'localhost', port: 6379 },
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 },
    removeOnComplete: { age: 86400 }, // Keep for 24h
    removeOnFail: { age: 604800 },    // Keep failed for 7d
  },
});

// Add a job
await emailQueue.add('welcome', {
  to: 'user@example.com',
  subject: 'Welcome!',
  template: 'welcome',
}, {
  priority: 1, // Lower = higher priority
  delay: 5000, // Delay 5 seconds
});

// Add a recurring job
await emailQueue.upsertJobScheduler(
  'daily-digest',
  { pattern: '0 9 * * *' }, // Every day at 9am
  { name: 'digest', data: {} },
);
```

### Worker

```typescript
import { Worker } from 'bullmq';

const worker = new Worker('email', async (job) => {
  switch (job.name) {
    case 'welcome':
      await sendWelcomeEmail(job.data);
      break;
    case 'digest':
      await sendDigestEmail(job.data);
      break;
  }
}, {
  connection: { host: 'localhost', port: 6379 },
  concurrency: 5,
  limiter: { max: 10, duration: 1000 }, // Max 10 jobs/sec
});

worker.on('completed', (job) => console.log(`Job ${job.id} completed`));
worker.on('failed', (job, err) => console.error(`Job ${job?.id} failed:`, err));
```

### NestJS Processor

```typescript
import { Processor, WorkerHost } from '@nestjs/bullmq';
import { Job } from 'bullmq';

@Processor('email')
export class EmailProcessor extends WorkerHost {
  async process(job: Job) {
    switch (job.name) {
      case 'welcome':
        return this.sendWelcome(job.data);
      case 'digest':
        return this.sendDigest(job.data);
    }
  }

  private async sendWelcome(data: { to: string }) {
    // Send email logic
  }

  private async sendDigest(data: Record<string, unknown>) {
    // Digest logic
  }
}
```

## Performance Best Practices

### 1. Use Pipelines for Batch Operations

```typescript
const pipeline = redis.pipeline();
ids.forEach((id) => pipeline.get(`user:${id}`));
const results = await pipeline.exec();
```

### 2. Use Hash for Structured Data

```typescript
// Instead of JSON serialization for partial reads
await redis.hset('user:123', { name: 'Alice', email: 'a@b.com', plan: 'pro' });
const plan = await redis.hget('user:123', 'plan'); // Read just one field
```

### 3. Set TTLs on Everything

Never cache without a TTL. Memory is finite.

```typescript
// Always use SETEX or SET with EX
await redis.setex(key, 300, value); // 5 minutes
// Never just SET without expiry in cache scenarios
```

### 4. Use Key Prefixes and Namespaces

```typescript
const CACHE_PREFIX = 'cache:';
const SESSION_PREFIX = 'sess:';
const RATE_PREFIX = 'rl:';

// Makes SCAN patterns efficient and avoids collisions
await redis.setex(`${CACHE_PREFIX}user:${id}`, 300, data);
```

### 5. Monitor Memory Usage

```typescript
const info = await redis.info('memory');
// Parse used_memory_human, maxmemory, eviction policy
```

### 6. Configure Eviction Policy

```
# redis.conf or via CONFIG SET
maxmemory 256mb
maxmemory-policy allkeys-lru
```

For caching: use `allkeys-lru` or `volatile-lru`.
For sessions/queues: use `noeviction` (you don't want to lose data).

## Common Pitfalls

1. **Sharing pub/sub connections** — A subscribed connection can't run other commands. Always use a separate connection.
2. **No TTL on cache keys** — Leads to memory exhaustion. Always set expiry.
3. **Using KEYS in production** — `KEYS *` blocks Redis. Use `SCAN` instead.
4. **Caching null results** — Cache misses too (short TTL) to prevent repeated DB queries for non-existent data.
5. **Not handling connection errors** — Redis going down shouldn't crash your app. Degrade gracefully.

```typescript
redis.on('error', (err) => {
  console.error('Redis connection error:', err);
  // Don't throw — let the app fall back to DB
});
```

## References

- [ioredis GitHub](https://github.com/redis/ioredis)
- [BullMQ Documentation](https://docs.bullmq.io/)
- [Redis Commands](https://redis.io/commands/)
- [NestJS Queues](https://docs.nestjs.com/techniques/queues)
