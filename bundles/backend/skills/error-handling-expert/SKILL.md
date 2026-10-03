---
name: error-handling-expert
description: Designs error handling, exception filters, error responses, logging, and recovery for React, Next.js, and NestJS. Use when implementing or reviewing error flows.
metadata:
  version: "2.2.2"
  tags: "errors, reliability, architecture"
when_to_use: "error boundaries, retry logic"
---

# Error Handling Expert Skill

## When to Use

- Implementing error handling
- Creating exception filters
- Designing error responses
- Setting up error logging
- Implementing error recovery
- Handling async errors
- Creating error boundaries
- Implementing retry logic

## Project Context Discovery

Before providing guidance:

1. Check `.agents/memory/` for project architecture and error patterns
2. Review existing exception filters
3. Check for error monitoring (Sentry, Rollbar)
4. Review logging libraries (Winston, Pino)

## Core Principles

### Error Types

**Application Errors:** 400, 401, 403, 404, 409, 422
**System Errors:** 500, 502, 503, 504

### Error Response Format

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

## Quick Patterns

### NestJS Exception Filter

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    // Log, format, respond
  }
}
```

### React Error Boundary

```typescript
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log to monitoring
  }
}
```

### Retry with Backoff

```typescript
async function retryWithBackoff<T>(fn, maxRetries = 3): Promise<T>
```

## Best Practices

- User-friendly messages, no sensitive info
- Log all errors with context
- Integrate error monitoring (Sentry)
- Implement retry logic and circuit breakers
- Provide fallback values
- Test error cases

## Recovery Strategies

1. **Retry Logic** - Exponential backoff
2. **Circuit Breaker** - Prevent cascade failures
3. **Fallback Values** - Graceful degradation

---

**For complete exception filter implementations, custom exceptions, validation pipe setup, error boundaries, circuit breaker pattern, logging integration, and database/API error patterns, see:** `references/full-guide.md`
