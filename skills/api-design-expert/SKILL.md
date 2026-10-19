---
name: api-design-expert
description: "Designs RESTful APIs for NestJS: endpoints, OpenAPI/Swagger docs, versioning, error responses, DTOs, and pagination. Use when designing or documenting API endpoints."
metadata:
  version: "2.2.4"
  tags: "api, rest, design"
when_to_use: "filtering, sorting"
---

# API Design Expert

Use when designing new endpoints or RESTful APIs, writing OpenAPI/Swagger documentation, implementing versioning, designing error responses, creating DTOs and validation, or implementing pagination, filtering, and sorting.

## Discover project context first

1. Check the repo's memory/instructions files (for example `.agents/memory/`, `AGENTS.md`, `CLAUDE.md`) for API patterns and architecture notes.
2. Review existing controllers and DTOs.
3. Check for an OpenAPI/Swagger setup.
4. Review the versioning strategy.

Follow what the project already does unless the user asks to change it.

## Core principles

### RESTful design

```typescript
// Use nouns, plural, hierarchical
GET    /api/users
GET    /api/users/:id
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id
GET    /api/users/:id/posts
```

### HTTP status codes

- `200 OK` / `201 Created` / `204 No Content`
- `400 Bad Request` / `401 Unauthorized` / `403 Forbidden`
- `404 Not Found` / `409 Conflict` / `500 Internal Server Error`

### Response format

```typescript
// Single resource
{ "data": {...}, "meta": {...} }

// List with pagination
{ "data": [...], "pagination": { "page", "limit", "total" } }
```

### Error format

```typescript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [...],
    "timestamp": "...",
    "path": "/api/users"
  }
}
```

## Best practices

- Consistent naming conventions
- Validate all inputs with DTOs
- OpenAPI/Swagger documentation
- Authentication on all endpoints
- Pagination for lists
- Version APIs from the start

## Full guide

For complete DTO examples, pagination/filtering/sorting patterns, versioning strategies, OpenAPI setup, CRUD controller patterns, nested resources, bulk operations, and anti-patterns, see [references/full-guide.md](references/full-guide.md).
