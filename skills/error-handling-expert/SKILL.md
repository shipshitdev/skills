---
name: error-handling-expert
description: Designs error handling, exception filters, error responses, logging, and recovery for React, Next.js, and NestJS. Use when implementing or reviewing error flows.
metadata:
  version: "2.2.4"
  tags: "errors, reliability, architecture"
when_to_use: "error boundaries, retry logic"
---

# Error Handling Expert

## When to use

- Implementing or reviewing error handling and recovery
- Creating NestJS exception filters or React error boundaries
- Designing error responses and error logging
- Handling async errors, implementing retry logic

## Discover project context first

1. Read the repo's memory/instructions files (CLAUDE.md, AGENTS.md, `.agents/memory/` if present) for architecture and error patterns.
2. Review existing exception filters and boundaries.
3. Check for error monitoring (Sentry, Rollbar).
4. Check the logging library (Winston, Pino).

Follow what the repo already does before adding a new pattern. In the Next.js App Router, route-level boundaries use `error.tsx` / `global-error.tsx`.

## Core principles

**Application errors:** 400, 401, 403, 404, 409, 422. **System errors:** 500, 502, 503, 504.

Error response format:

```typescript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [...],
    "timestamp": "2025-01-01T00:00:00Z",
    "path": "/api/users",
    "requestId": "req-123456"
  }
}
```

## Quick patterns

NestJS exception filter:

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    // Log, format, respond
  }
}
```

React error boundary:

```typescript
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log to monitoring
  }
}
```

Retry with backoff:

```typescript
async function retryWithBackoff<T>(fn, maxRetries = 3): Promise<T>
```

These are skeletons; full implementations are in `references/full-guide.md`.

## Best practices

- User-friendly messages; no sensitive information in responses.
- Log every error with context.
- Integrate error monitoring (Sentry).
- Add retries and circuit breakers where appropriate; provide fallback values.
- Test error cases.

## Recovery strategies

1. **Retry logic:** exponential backoff.
2. **Circuit breaker:** prevent cascade failures.
3. **Fallback values:** graceful degradation.

For complete exception filters, custom exceptions, validation pipe setup, error boundaries, circuit breaker, logging integration and database/API error patterns, read `references/full-guide.md`.
