# NestJS Queue Architect - Full Guide

## Technology Stack

- **BullMQ**: 5.61.0 (Redis-backed job queue)
- **@nestjs/bullmq**: 12.0.0 (NestJS 12)
- **@bull-board/nestjs**: 6.13.1 (Queue monitoring UI)
- **Redis**: ioredis 5.8.2

## Core Patterns

### 1. Queue Service Pattern

**Typical Location**: `[project]/src/queues/*-queue.service.ts`

Queue services encapsulate job creation logic and maintain consistent retry/priority policies.

```typescript
import { InjectQueue } from '@nestjs/bullmq';
import { Injectable, Logger } from '@nestjs/common';
import { Queue } from 'bullmq';

@Injectable()
export class VideoQueueService {
  private readonly logger = new Logger(VideoQueueService.name);

  constructor(
    @InjectQueue(QUEUE_NAMES.VIDEO_PROCESSING)
    private videoQueue: Queue<VideoJobData>,
  ) {}

  async addResizeJob(data: VideoJobData) {
    const job = await this.videoQueue.add(JOB_TYPES.RESIZE_VIDEO, data, {
      priority: data.priority || JOB_PRIORITY.NORMAL,
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000,
      },
    });

    this.logger.log(
      `Added resize job ${job.id} for ingredient ${data.ingredientId}`,
    );
    return job;
  }

  async addMergeJob(data: VideoJobData) {
    const job = await this.videoQueue.add(JOB_TYPES.MERGE_VIDEOS, data, {
      priority: data.priority || JOB_PRIORITY.NORMAL,
      attempts: 2, // Lower for resource-intensive ops
      backoff: {
        type: 'exponential',
        delay: 5000, // Longer delay for heavy jobs
      },
    });

    this.logger.log(
      `Added merge job ${job.id} for ${data.params.sourceIds?.length} videos`,
    );
    return job;
  }

  // Queue maintenance
  async clean(grace: number = 3600000) {
    await this.videoQueue.clean(grace, 0, 'completed');
    await this.videoQueue.clean(grace * 2, 0, 'failed'); // Keep failed jobs longer
  }
}
```

**Key Principles**:

- One service per queue type
- Encapsulate job options (attempts, backoff, priority)
- Log every job creation with meaningful context
- Adjust retry strategy based on job type (heavy vs lightweight)
- Implement queue cleanup methods

### 2. Queue Constants Pattern

**Typical Location**: `[project]/src/queues/queue.constants.ts`

```typescript
export const QUEUE_NAMES = {
  VIDEO_PROCESSING: 'video-processing',
  IMAGE_PROCESSING: 'image-processing',
  FILE_PROCESSING: 'file-processing',
  TASK_PROCESSING: 'task-processing',
} as const;

export const JOB_TYPES = {
  // Video operations
  RESIZE_VIDEO: 'resize-video',
  MERGE_VIDEOS: 'merge-videos',
  ADD_CAPTIONS: 'add-captions',
  VIDEO_TO_GIF: 'video-to-gif',
  TRIM_VIDEO: 'trim-video',

  // Image operations
  IMAGE_TO_VIDEO: 'image-to-video',
  KEN_BURNS_EFFECT: 'ken-burns-effect',
  RESIZE_IMAGE: 'resize-image',

  // File operations
  DOWNLOAD_FILE: 'download-file',
  UPLOAD_TO_S3: 'upload-to-s3',
  CLEANUP_TEMP_FILES: 'cleanup-temp-files',
} as const;

export const JOB_PRIORITY = {
  HIGH: 1, // Metadata retrieval, user-facing
  NORMAL: 5, // Standard processing
  LOW: 10, // GIF conversion, background tasks
} as const;

export type QueueName = (typeof QUEUE_NAMES)[keyof typeof QUEUE_NAMES];
export type JobType = (typeof JOB_TYPES)[keyof typeof JOB_TYPES];
export type JobPriority = (typeof JOB_PRIORITY)[keyof typeof JOB_PRIORITY];
```

### 3. Queue Module Configuration

**Typical Location**: `[project]/src/queues/queues.module.ts`

```typescript
import { BullModule } from '@nestjs/bullmq';
import { Module } from '@nestjs/common';

@Module({
  imports: [
    BullModule.registerQueue(
      {
        name: QUEUE_NAMES.VIDEO_PROCESSING,
        defaultJobOptions: {
          attempts: 3,
          backoff: {
            type: 'exponential',
            delay: 2000,
          },
          removeOnComplete: 100, // Keep last 100 completed jobs
          removeOnFail: 50, // Keep last 50 failed jobs for debugging
        },
      },
      {
        name: QUEUE_NAMES.IMAGE_PROCESSING,
        defaultJobOptions: {
          attempts: 3,
          backoff: {
            type: 'exponential',
            delay: 1000, // Faster retry for lighter operations
          },
          removeOnComplete: 100,
          removeOnFail: 50,
        },
      },
    ),
  ],
  providers: [VideoQueueService, ImageQueueService, FileQueueService],
  exports: [VideoQueueService, ImageQueueService, FileQueueService],
})
export class QueuesModule {}
```

### 4. Processor Pattern (WorkerHost)

**Typical Location**: `[project]/src/processors/[type].processor.ts`

```typescript
import { Processor, WorkerHost } from '@nestjs/bullmq';
import { Logger } from '@nestjs/common';
import { Job } from 'bullmq';

@Processor(QUEUE_NAMES.VIDEO_PROCESSING)
export class VideoProcessor extends WorkerHost {
  private readonly logger = new Logger(VideoProcessor.name);

  constructor(
    private ffmpegService: FFmpegService,
    private s3Service: S3Service,
    private webSocketService: WebSocketService,
    private redisService: RedisService,
  ) {
    super();
  }

  async process(job: Job<VideoJobData>): Promise<JobResult> {
    this.logger.log(`Processing video job ${job.id}: ${job.name}`);

    switch (job.name) {
      case JOB_TYPES.MERGE_VIDEOS:
        return await this.handleMerge(job);
      case JOB_TYPES.RESIZE_VIDEO:
        return await this.handleResize(job);
      case JOB_TYPES.TRIM_VIDEO:
        return await this.handleTrim(job);
      default:
        throw new Error(`Unknown video job type: ${job.name}`);
    }
  }

  private async handleResize(job: Job<VideoJobData>): Promise<JobResult> {
    const { ingredientId, params, metadata, userId, organizationId } = job.data;

    try {
      // 1. Download input from S3
      const tempPath = this.ffmpegService.getTempPath('resize', ingredientId);
      const inputPath = path.join(tempPath, 'input.mp4');

      if (params.s3Key) {
        await this.s3Service.downloadFile(params.s3Key, inputPath);
      }

      // 2. Process with progress updates
      const outputPath = path.join(tempPath, 'output.mp4');
      await this.ffmpegService.resizeVideo(
        inputPath,
        outputPath,
        params.width || 1080,
        params.height || 1920,
        (progress) => {
          this.webSocketService.emitProgress(
            metadata.websocketUrl,
            this.convertToJobProgress(progress),
            userId,
          );
        },
      );

      // 3. Upload result
      const s3Key = this.s3Service.generateS3Key('videos', ingredientId);
      await this.s3Service.uploadFile(s3Key, outputPath, 'video/mp4');

      // 4. Cleanup temp files
      this.ffmpegService.cleanupTempFiles(ingredientId, 'resize');

      // 5. Publish completion event
      const result = {
        ingredientId,
        s3Key,
        url: this.s3Service.getPublicUrl(s3Key),
      };
      await this.publishVideoCompletion(
        ingredientId,
        userId,
        organizationId,
        'completed',
        result,
      );

      return { success: true, outputPath, s3Key };
    } catch (error: any) {
      this.logger.error(`Resize job failed: ${error?.message}`);

      // Emit error to WebSocket
      this.webSocketService.emitError(
        metadata.websocketUrl,
        error?.message,
        userId,
      );

      // Publish failure event
      await this.publishVideoCompletion(
        ingredientId,
        userId,
        organizationId,
        'failed',
        null,
        error?.message,
      );

      throw error; // Re-throw for BullMQ retry logic
    }
  }

  private async publishVideoCompletion(
    ingredientId: string,
    userId: string,
    organizationId: string,
    status: 'completed' | 'failed',
    result?: any,
    error?: string,
  ) {
    await this.redisService.publish('video-processing-complete', {
      ingredientId,
      userId,
      organizationId,
      status,
      result,
      error,
      timestamp: new Date().toISOString(),
    });
  }
}
```

**Processor Best Practices**:

1. **Switch-based routing**: Use job.name to route to handlers
2. **Structured error handling**: Catch, log, emit to WebSocket, publish to Redis, then re-throw
3. **Always cleanup**: Use try/catch/finally for temp file cleanup
4. **Progress updates**: Emit real-time progress via WebSocket for long-running jobs
5. **Event publishing**: Use Redis pub/sub to notify other services (API) of job completion
6. **Idempotency**: Design handlers to be safe if retried (check if output already exists)

### 5. Job Data Interfaces

```typescript
export interface VideoJobData {
  ingredientId: string;
  userId: string;
  organizationId: string;
  priority?: JobPriority;

  params: {
    s3Key?: string;
    inputPath?: string;
    width?: number;
    height?: number;
    sourceIds?: string[];
    captionContent?: string;
    startTime?: number;
    endTime?: number;
    duration?: number;
    text?: string;
    position?: 'top' | 'center' | 'bottom';
  };

  metadata: {
    websocketUrl: string;
    room?: string;
  };
}

export interface JobResult {
  success: boolean;
  outputPath?: string;
  s3Key?: string;
  metadata?: any;
  error?: string;
}
```

### 6. Testing Queue Services

**Typical Location**: `[project]/src/queues/[queue].service.spec.ts`

```typescript
import { getQueueToken } from '@nestjs/bullmq';
import { Test, TestingModule } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('VideoQueueService', () => {
  let service: VideoQueueService;
  let mockQueue: any;

  beforeEach(async () => {
    mockQueue = {
      add: vi.fn().mockResolvedValue({ id: 'test-job-id' }),
      getJob: vi.fn(),
      getJobCounts: vi.fn(),
      clean: vi.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        VideoQueueService,
        {
          provide: getQueueToken(QUEUE_NAMES.VIDEO_PROCESSING),
          useValue: mockQueue,
        },
      ],
    }).compile();

    service = module.get<VideoQueueService>(VideoQueueService);
  });

  it('should queue a resize job with correct options', async () => {
    const jobData: VideoJobData = {
      ingredientId: 'ing-123',
      userId: 'user-456',
      organizationId: 'org-789',
      params: { width: 1920, height: 1080 },
      metadata: { websocketUrl: 'ws://localhost' },
    };

    const result = await service.addResizeJob(jobData);

    expect(mockQueue.add).toHaveBeenCalledWith(
      JOB_TYPES.RESIZE_VIDEO,
      jobData,
      expect.objectContaining({
        priority: 5,
        attempts: 3,
        backoff: { type: 'exponential', delay: 2000 },
      }),
    );
    expect(result.id).toBe('test-job-id');
  });

  it('should clean completed and failed jobs', async () => {
    await service.clean(3600000);

    expect(mockQueue.clean).toHaveBeenCalledWith(3600000, 0, 'completed');
    expect(mockQueue.clean).toHaveBeenCalledWith(7200000, 0, 'failed');
  });
});
```

## Queue Architecture Decisions

### When to Create a New Queue

Create separate queues when:

1. **Different concurrency needs**: Video processing (2 workers) vs image processing (10 workers)
2. **Different resource requirements**: CPU-intensive vs I/O-intensive
3. **Different priority levels**: User-facing vs background tasks
4. **Different failure modes**: Transient vs permanent failures

### Job Priority Guidelines

```typescript
export const JOB_PRIORITY = {
  HIGH: 1, // User-facing: metadata retrieval, thumbnail generation
  NORMAL: 5, // Standard: video resize, image conversion
  LOW: 10, // Background: cleanup, GIF conversion, analytics
} as const;
```

### Retry Strategy by Job Type

| Job Type       | Attempts | Delay  | Reason                              |
| -------------- | -------- | ------ | ----------------------------------- |
| Resize video   | 3        | 2000ms | Transient S3/network issues         |
| Merge videos   | 2        | 5000ms | Resource-intensive, longer recovery |
| Get metadata   | 2        | 1000ms | Fast operation, fail quickly        |
| GIF conversion | 3        | 2000ms | Low priority, can retry             |
| Cleanup files  | 5        | 1000ms | Must succeed, low cost              |

### Queue Monitoring with Bull Board

```typescript
import { BullBoardModule } from '@bull-board/nestjs';
import { ExpressAdapter } from '@bull-board/express';
import { BullMQAdapter } from '@bull-board/api/bullMQAdapter';

@Module({
  imports: [
    BullBoardModule.forRoot({
      route: '/queues',
      adapter: ExpressAdapter,
    }),
    BullBoardModule.forFeature({
      name: QUEUE_NAMES.VIDEO_PROCESSING,
      adapter: BullMQAdapter,
    }),
  ],
})
export class AppModule {}
```

Access queue dashboard at: `http://localhost:3000/queues`

## Common Pitfalls and Solutions

### 1. Memory Leaks from Completed Jobs

**Problem**: Redis fills up with millions of completed jobs.

**Solution**: Always set `removeOnComplete` and `removeOnFail`:

```typescript
defaultJobOptions: {
  removeOnComplete: 100,  // Keep last 100 for debugging
  removeOnFail: 50,
}
```

### 2. Job Timeout Issues

**Problem**: Long-running jobs timeout before completion.

**Solution**: Set appropriate timeout based on job type:

```typescript
await this.videoQueue.add(JOB_TYPES.MERGE_VIDEOS, data, {
  timeout: 600000, // 10 minutes for heavy operations
});
```

### 3. Lost Progress Updates

**Problem**: WebSocket progress updates stop when job retries.

**Solution**: Track progress in Redis, resume on retry:

```typescript
// Before starting
await this.redisService.set(`job:${job.id}:progress`, 0);

// During processing
await this.redisService.set(`job:${job.id}:progress`, progress.percent);

// On retry, check last progress
const lastProgress = await this.redisService.get(`job:${job.id}:progress`);
```

### 4. Race Conditions with Multiple Processors

**Problem**: Two processors handle the same job.

**Solution**: BullMQ handles this automatically, but ensure idempotent handlers:

```typescript
// Check if already processed
const s3Key = this.s3Service.generateS3Key('videos', ingredientId);
const exists = await this.s3Service.exists(s3Key);
if (exists) {
  this.logger.warn(`Video ${ingredientId} already processed, skipping`);
  return { success: true, s3Key };
}
```

## Implementation Checklist

When implementing a new queue:

- [ ] Define queue name in `queue.constants.ts`
- [ ] Define job types with descriptive names
- [ ] Create queue service with typed job data interfaces
- [ ] Implement processor extending `WorkerHost`
- [ ] Add switch-case routing in `process()` method
- [ ] Implement structured error handling (log, emit, publish, throw)
- [ ] Add progress updates for long-running jobs
- [ ] Configure appropriate retry strategy
- [ ] Set `removeOnComplete` and `removeOnFail`
- [ ] Write unit tests for queue service
- [ ] Add queue to Bull Board monitoring
- [ ] Document job data schema
- [ ] Test idempotency and retry behavior

## Performance Tips

1. **Batch S3 operations**: Download multiple files in parallel
2. **Stream large files**: Don't load entire video into memory
3. **Use Redis for job state**: Store progress, intermediate results
4. **Set concurrency limits**: Prevent resource exhaustion
5. **Monitor queue metrics**: Track processing time, failure rate
6. **Clean old jobs regularly**: Schedule cleanup cron job
7. **Use job priorities wisely**: Don't starve low-priority jobs
8. **Implement circuit breakers**: Pause queue on repeated failures

## Redis Pub/Sub Integration

```typescript
// In processor
await this.redisService.publish('video-processing-complete', {
  ingredientId,
  userId,
  organizationId,
  status: 'completed',
  result: { s3Key, url },
  timestamp: new Date().toISOString(),
});

// In API app (listener)
@Injectable()
export class VideoEventListener implements OnModuleInit {
  constructor(private redisService: RedisService) {}

  async onModuleInit() {
    await this.redisService.subscribe(
      'video-processing-complete',
      (message) => {
        const data = JSON.parse(message);
        // Update database, send notifications, etc.
        await this.videosService.updateStatus(data.ingredientId, data.status);
      },
    );
  }
}
```
