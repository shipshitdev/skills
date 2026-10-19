---
name: nestjs-queue-architect
description: Designs BullMQ queues, processors, and async job workflows in NestJS for video/image processing. Use when building queue processors or media pipelines.
metadata:
  version: "2.2.4"
  technology: BullMQ 5.61.0 with NestJS 12.1.2
  expertise_level: senior
  last_updated: "2025-10-22"
  tags: "nestjs, queues, async"
when_to_use: "BullMQ, job processor, bull-board"
---

# NestJS Queue Architect - BullMQ Expert

Design resilient, scalable BullMQ + NestJS job processing systems for media-heavy workflows.

## Technology Stack

Versions below were last recorded in 2025-10 and may be stale; check the repo's
`package.json` and the registry before relying on them (verify).

- **BullMQ**: 5.61.0 (Redis-backed job queue)
- **@nestjs/bullmq**: 12.0.0 (NestJS 12)
- **@bull-board/nestjs**: 6.13.1 (Queue monitoring UI)

## Project Context Discovery

Before implementing:

1. Check the repo's memory/instructions files (for example CLAUDE.md or AGENTS.md) for queue conventions
2. Review existing queue services and constants
3. Look for a project-specific queue skill and prefer its conventions

## Core Patterns

### Queue Constants

```typescript
export const QUEUE_NAMES = {
  VIDEO: 'video-processing',
  IMAGE: 'image-processing',
} as const;

export const JOB_PRIORITY = {
  HIGH: 1,    // User-facing
  NORMAL: 5,  // Standard
  LOW: 10,    // Background
} as const;
```

### Queue Service

```typescript
@Injectable()
export class VideoQueueService {
  constructor(@InjectQueue(QUEUE_NAMES.VIDEO) private queue: Queue) {}

  async addJob(data: VideoJobData) {
    return this.queue.add(JOB_TYPES.RESIZE, data, {
      priority: JOB_PRIORITY.NORMAL,
      attempts: 3,
      backoff: { type: 'exponential', delay: 2000 },
    });
  }
}
```

### Processor (WorkerHost)

```typescript
@Processor(QUEUE_NAMES.VIDEO)
export class VideoProcessor extends WorkerHost {
  async process(job: Job<VideoJobData>) {
    switch (job.name) {
      case JOB_TYPES.RESIZE: return this.handleResize(job);
      case JOB_TYPES.MERGE: return this.handleMerge(job);
      default: throw new Error(`Unknown job: ${job.name}`);
    }
  }
}
```

## Key Principles

1. **One service per queue type** - Encapsulate job options
2. **Switch-based routing** - Route by `job.name`
3. **Structured error handling** - Log, emit WebSocket, publish Redis, re-throw
4. **Always cleanup** - Temp files in try/finally
5. **Idempotent handlers** - Safe to retry

## Queue Configuration

```typescript
BullModule.registerQueue({
  name: QUEUE_NAMES.VIDEO,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: 100,  // Prevent Redis bloat
    removeOnFail: 50,
  },
});
```

## Retry Strategy

| Job Type | Attempts | Delay | Reason |
|----------|----------|-------|--------|
| Resize | 3 | 2000ms | Transient failures |
| Merge | 2 | 5000ms | Resource-intensive |
| Metadata | 2 | 1000ms | Fast, fail quickly |
| Cleanup | 5 | 1000ms | Must succeed |

## Common Pitfalls

- **Memory leaks**: Always set `removeOnComplete/Fail`
- **Timeouts**: Bound heavy handlers explicitly (verify whether your BullMQ version supports a per-job timeout; otherwise enforce it inside the handler)
- **Race conditions**: Make handlers idempotent

## Further reading

**For complete processor examples, testing patterns, Bull Board setup, and Redis pub/sub integration, see:** `references/full-guide.md`
