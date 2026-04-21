# API Design Expert - Full Guide

## Core API Design Principles

### 1. RESTful Design

**Resource-Based URLs:**

- Use nouns, not verbs
- Use plural nouns
- Hierarchical resources
- Consistent naming

```typescript
// GOOD: RESTful
GET    /api/users
GET    /api/users/:id
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id

GET    /api/users/:id/posts
POST   /api/users/:id/posts

// BAD: Not RESTful
GET    /api/getUsers
POST   /api/createUser
GET    /api/userPosts/:userId
```

**HTTP Methods:**

- `GET`: Retrieve resources
- `POST`: Create resources
- `PUT`: Update entire resource
- `PATCH`: Partial update
- `DELETE`: Delete resource

**HTTP Status Codes:**

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success, no body
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `500 Internal Server Error`: Server error

### 2. API Versioning

**URL Versioning (Recommended):**

```typescript
// Version in URL
GET /api/v1/users
GET /api/v2/users

// NestJS implementation
@Controller("api/v1/users")
export class UsersV1Controller {}

@Controller("api/v2/users")
export class UsersV2Controller {}
```

**Header Versioning:**

```typescript
// Version in header
Accept: application/vnd.api+json; version=1

// NestJS implementation
@ApiVersion("1")
@Controller("api/users")
export class UsersController {}
```

### 3. Request/Response Design

**Request Bodies:**

```typescript
// DTO with validation
export class CreateUserDto {
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @IsString()
  @MinLength(8)
  password: string;

  @IsString()
  @IsOptional()
  name?: string;
}

@Post()
async create(@Body() dto: CreateUserDto) {
  return this.usersService.create(dto);
}
```

**Response Format:**

```typescript
// Consistent response format
{
  "data": {
    "id": "123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "meta": {
    "timestamp": "2025-01-01T00:00:00Z"
  }
}

// For lists
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### 4. Pagination, Filtering, Sorting

**Pagination:**

```typescript
export class PaginationDto {
  @IsInt()
  @Min(1)
  @IsOptional()
  @Type(() => Number)
  page?: number = 1;

  @IsInt()
  @Min(1)
  @Max(100)
  @IsOptional()
  @Type(() => Number)
  limit?: number = 20;
}

@Get()
async findAll(@Query() pagination: PaginationDto) {
  return this.usersService.findAll(pagination);
}
```

**Filtering:**

```typescript
export class FilterUsersDto extends PaginationDto {
  @IsString()
  @IsOptional()
  email?: string;

  @IsString()
  @IsOptional()
  organization?: string;
}

@Get()
async findAll(@Query() filters: FilterUsersDto) {
  return this.usersService.findAll(filters);
}
```

**Sorting:**

```typescript
export class SortUsersDto extends FilterUsersDto {
  @IsString()
  @IsOptional()
  @IsIn(["createdAt", "email", "name"])
  sortBy?: string = "createdAt";

  @IsString()
  @IsOptional()
  @IsIn(["asc", "desc"])
  sortOrder?: "asc" | "desc" = "desc";
}
```

### 5. Error Handling

**Consistent Error Format:**

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
    "path": "/api/users"
  }
}
```

**Exception Filters:**

```typescript
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status = exception.getStatus();

    response.status(status).json({
      error: {
        code: exception.name,
        message: exception.message,
        timestamp: new Date().toISOString(),
        path: ctx.getRequest().url,
      },
    });
  }
}
```

### 6. OpenAPI/Swagger Documentation

**Setup:**

```typescript
// main.ts
const config = new DocumentBuilder()
  .setTitle("API Documentation")
  .setDescription("API description")
  .setVersion("1.0")
  .addBearerAuth()
  .build();

const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup("api/docs", app, document);
```

**DTO Documentation:**

```typescript
export class CreateUserDto {
  @ApiProperty({ example: "user@example.com" })
  @IsEmail()
  email: string;

  @ApiProperty({ example: "password123", minLength: 8 })
  @IsString()
  @MinLength(8)
  password: string;
}
```

**Endpoint Documentation:**

```typescript
@ApiOperation({ summary: 'Create a new user' })
@ApiResponse({ status: 201, description: 'User created' })
@ApiResponse({ status: 400, description: 'Validation error' })
@Post()
async create(@Body() dto: CreateUserDto) {
  return this.usersService.create(dto);
}
```

## API Design Patterns

### 1. CRUD Operations

```typescript
@Controller("api/users")
export class UsersController {
  @Get()
  async findAll(@Query() filters: FilterUsersDto) {
    return this.usersService.findAll(filters);
  }

  @Get(":id")
  async findOne(@Param("id") id: string) {
    return this.usersService.findOne(id);
  }

  @Post()
  async create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Put(":id")
  async update(@Param("id") id: string, @Body() dto: UpdateUserDto) {
    return this.usersService.update(id, dto);
  }

  @Patch(":id")
  async partialUpdate(
    @Param("id") id: string,
    @Body() dto: PartialUpdateUserDto
  ) {
    return this.usersService.partialUpdate(id, dto);
  }

  @Delete(":id")
  async remove(@Param("id") id: string) {
    return this.usersService.remove(id);
  }
}
```

### 2. Nested Resources

```typescript
@Controller("api/users/:userId/posts")
export class UserPostsController {
  @Get()
  async findAll(@Param("userId") userId: string) {
    return this.postsService.findByUser(userId);
  }

  @Post()
  async create(@Param("userId") userId: string, @Body() dto: CreatePostDto) {
    return this.postsService.create(userId, dto);
  }
}
```

### 3. Bulk Operations

```typescript
@Post('bulk')
async createBulk(@Body() dto: CreateUsersBulkDto) {
  return this.usersService.createBulk(dto.users);
}

@Delete('bulk')
async deleteBulk(@Body() dto: DeleteUsersBulkDto) {
  return this.usersService.deleteBulk(dto.ids);
}
```

### 4. Search Endpoints

```typescript
@Get('search')
async search(@Query() query: SearchUsersDto) {
  return this.usersService.search(query);
}
```

## Best Practices

### 1. Consistency

- Consistent naming conventions
- Consistent response formats
- Consistent error handling
- Consistent status codes

### 2. Validation

- Validate all inputs
- Use DTOs with validation decorators
- Return clear validation errors
- Validate at controller level

### 3. Documentation

- OpenAPI/Swagger documentation
- Clear endpoint descriptions
- Example requests/responses
- Authentication requirements documented

### 4. Security

- Authentication on all endpoints
- Authorization checks
- Input validation
- Rate limiting
- CORS configured

### 5. Performance

- Pagination for lists
- Filtering and sorting
- Caching where appropriate
- Database query optimization

### 6. Versioning

- Version APIs from the start
- Maintain backward compatibility
- Deprecation strategy
- Migration path for breaking changes

## Common Anti-Patterns to Avoid

### 1. Verb-Based URLs

```typescript
// BAD
GET /api/getUsers
POST /api/createUser

// GOOD
GET /api/users
POST /api/users
```

### 2. Inconsistent Response Formats

```typescript
// BAD: Inconsistent
{ users: [...] }
{ data: [...] }
{ items: [...] }

// GOOD: Consistent
{ data: [...] }
```

### 3. Poor Error Messages

```typescript
// BAD
{ error: "Error" }

// GOOD
{
  error: {
    code: "VALIDATION_ERROR",
    message: "Validation failed",
    details: [...]
  }
}
```

### 4. No Pagination

```typescript
// BAD: Returns all records
GET /api/users

// GOOD: Paginated
GET /api/users?page=1&limit=20
```

## Resources

- RESTful API Design: https://restfulapi.net/
- OpenAPI Specification: https://swagger.io/specification/
- NestJS Documentation: https://docs.nestjs.com/
- HTTP Status Codes: https://httpstatuses.com/
