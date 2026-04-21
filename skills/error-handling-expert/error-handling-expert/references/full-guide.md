# Error Handling Expert - Full Guide

## Core Error Handling Principles

### 1. Error Types

**Application Errors:**

- Validation errors (400)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Conflict errors (409)
- Business logic errors (422)

**System Errors:**

- Server errors (500)
- Database errors (500)
- External service errors (502, 503)
- Timeout errors (504)

### 2. Error Response Format

**Consistent Error Structure:**

```typescript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "email must be an email"
      }
    ],
    "timestamp": "2025-01-01T00:00:00Z",
    "path": "/api/users",
    "requestId": "req-123456"
  }
}
```

### 3. Exception Filters (NestJS)

**Global Exception Filter:**

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();

    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    const message =
      exception instanceof HttpException
        ? exception.getResponse()
        : 'Internal server error';

    // Log error
    this.logger.error(
      `${request.method} ${request.url}`,
      exception instanceof Error ? exception.stack : exception,
    );

    response.status(status).json({
      error: {
        code: this.getErrorCode(exception),
        message: typeof message === 'string' ? message : (message as any).message,
        details: this.getErrorDetails(exception),
        timestamp: new Date().toISOString(),
        path: request.url,
        requestId: request.id,
      },
    });
  }
}
```

**HTTP Exception Filter:**

```typescript
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();
    const status = exception.getStatus();

    response.status(status).json({
      error: {
        code: exception.name,
        message: exception.message,
        details: exception.getResponse(),
        timestamp: new Date().toISOString(),
        path: request.url,
      },
    });
  }
}
```

### 4. Custom Exceptions

**Business Logic Exceptions:**

```typescript
export class UserNotFoundException extends HttpException {
  constructor(userId: string) {
    super(
      {
        code: 'USER_NOT_FOUND',
        message: `User with ID ${userId} not found`,
      },
      HttpStatus.NOT_FOUND,
    );
  }
}

export class EmailAlreadyExistsException extends HttpException {
  constructor(email: string) {
    super(
      {
        code: 'EMAIL_ALREADY_EXISTS',
        message: `Email ${email} is already registered`,
      },
      HttpStatus.CONFLICT,
    );
  }
}
```

**Usage:**

```typescript
async findOne(id: string) {
  const user = await this.userModel.findById(id);

  if (!user) {
    throw new UserNotFoundException(id);
  }

  return user;
}
```

### 5. Validation Error Handling

**Validation Pipe:**

```typescript
app.useGlobalPipes(
  new ValidationPipe({
    exceptionFactory: (errors) => {
      const formattedErrors = errors.map((error) => ({
        field: error.property,
        message: Object.values(error.constraints || {}).join(', '),
      }));

      return new BadRequestException({
        code: 'VALIDATION_ERROR',
        message: 'Validation failed',
        details: formattedErrors,
      });
    },
  }),
);
```

### 6. Async Error Handling

**Try-Catch in Async Functions:**

```typescript
async create(dto: CreateUserDto) {
  try {
    const user = await this.userModel.create(dto);
    return user;
  } catch (error) {
    if (error.code === 11000) {
      // Duplicate key error
      throw new EmailAlreadyExistsException(dto.email);
    }
    throw error;
  }
}
```

**Promise Error Handling:**

```typescript
async findAll() {
  return this.userModel
    .find({})
    .exec()
    .catch((error) => {
      this.logger.error('Failed to fetch users', error);
      throw new InternalServerErrorException('Failed to fetch users');
    });
}
```

### 7. Error Logging

**Structured Logging:**

```typescript
catch(exception: unknown, host: ArgumentsHost) {
  const ctx = host.switchToHttp();
  const request = ctx.getRequest();

  const logContext = {
    method: request.method,
    url: request.url,
    statusCode: status,
    userId: request.user?.id,
    organizationId: request.user?.organizationId,
    requestId: request.id,
    error: exception instanceof Error ? {
      name: exception.name,
      message: exception.message,
      stack: exception.stack,
    } : exception,
  };

  if (status >= 500) {
    this.logger.error('Server error', logContext);
  } else {
    this.logger.warn('Client error', logContext);
  }
}
```

**Error Monitoring Integration:**

```typescript
import * as Sentry from '@sentry/node';

catch(exception: unknown, host: ArgumentsHost) {
  // Log to Sentry for server errors
  if (status >= 500) {
    Sentry.captureException(exception, {
      tags: {
        endpoint: request.url,
        method: request.method,
      },
      user: {
        id: request.user?.id,
        organization: request.user?.organizationId,
      },
    });
  }
}
```

## React Error Handling

### Error Boundaries

**Class Component Error Boundary:**

```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to error monitoring
    Sentry.captureException(error, { contexts: { react: errorInfo } });
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

**Hook-Based Error Boundary:**

```typescript
function useErrorHandler(error?: Error) {
  useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);
}
```

### API Error Handling

**Error Handling Hook:**

```typescript
function useApiError() {
  const [error, setError] = useState<Error | null>(null);

  const handleError = useCallback((err: unknown) => {
    if (err instanceof Error) {
      setError(err);
    } else {
      setError(new Error('An unexpected error occurred'));
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
}
```

**API Call with Error Handling:**

```typescript
async function fetchUsers() {
  try {
    const response = await fetch('/api/users');

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.error.message, error.error.code);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      // Handle API error
      handleApiError(error);
    } else {
      // Handle network error
      handleNetworkError(error);
    }
    throw error;
  }
}
```

## Error Recovery Strategies

### 1. Retry Logic

**Exponential Backoff:**

```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  delay = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;

      await new Promise(resolve =>
        setTimeout(resolve, delay * Math.pow(2, i))
      );
    }
  }
  throw new Error('Max retries exceeded');
}
```

### 2. Circuit Breaker

**Circuit Breaker Pattern:**

```typescript
class CircuitBreaker {
  private failures = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private nextAttempt = Date.now();

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  private onFailure() {
    this.failures++;
    if (this.failures >= 5) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + 60000; // 1 minute
    }
  }
}
```

### 3. Fallback Values

**Fallback Strategy:**

```typescript
async function getUserWithFallback(id: string) {
  try {
    return await userService.findOne(id);
  } catch (error) {
    // Return cached user or default
    return cachedUser || getDefaultUser();
  }
}
```

## Best Practices

### 1. Error Messages

- ✅ User-friendly messages
- ✅ Don't expose sensitive information
- ✅ Include error codes for debugging
- ✅ Provide actionable guidance

### 2. Error Logging

- ✅ Log all errors
- ✅ Include context (user, request, etc.)
- ✅ Use structured logging
- ✅ Don't log sensitive data

### 3. Error Monitoring

- ✅ Integrate error monitoring (Sentry)
- ✅ Set up alerts for critical errors
- ✅ Track error rates
- ✅ Review error trends

### 4. Error Recovery

- ✅ Implement retry logic
- ✅ Use circuit breakers
- ✅ Provide fallback values
- ✅ Graceful degradation

### 5. Error Testing

- ✅ Test error cases
- ✅ Test error boundaries
- ✅ Test error recovery
- ✅ Test error logging

## Common Error Handling Patterns

### Database Errors

```typescript
catch(error) {
  if (error.code === 11000) {
    // Duplicate key
    throw new ConflictException('Resource already exists');
  }
  if (error.name === 'ValidationError') {
    throw new BadRequestException(error.message);
  }
  throw new InternalServerErrorException('Database error');
}
```

### External API Errors

```typescript
catch(error) {
  if (error.response) {
    // API responded with error
    throw new ExternalServiceException(
      error.response.data.message,
      error.response.status
    );
  }
  if (error.request) {
    // Request made but no response
    throw new ServiceUnavailableException('External service unavailable');
  }
  throw new InternalServerErrorException('Failed to call external service');
}
```

## Resources

- NestJS Exception Filters: https://docs.nestjs.com/exception-filters
- React Error Boundaries: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary
- Error Handling Best Practices: https://kentcdodds.com/blog/get-a-catch-block-error-message-with-typescript
