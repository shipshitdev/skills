---
name: api-design-expert
description: "Designs RESTful APIs for NestJS: endpoints, OpenAPI/Swagger docs, versioning, error responses, DTOs, and pagination. Use when designing or documenting API endpoints."
metadata:
  version: "2.2.4"
  tags: "api, rest, design"
when_to_use: "filtering, sorting"
---

# API Design Expert Skill

## When to Use

- Designing new API endpoints
- Creating RESTful APIs
- Writing OpenAPI/Swagger documentation
- Implementing API versioning
- Designing error responses
- Creating DTOs and validation
- Implementing pagination, filtering, sorting

## Project Context Discovery

Before providing guidance:

1. Check `.agents/memory/` for API patterns and architecture notes
2. Review existing controllers and DTOs
3. Check for OpenAPI/Swagger setup
4. Review versioning strategy

## Core Principles

### RESTful Design

```typescript
// Use nouns, plural, hierarchical
GET    /api/users
GET    /api/users/:id
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id
GET    /api/users/:id/posts
```

### HTTP Status Codes

- `200 OK` / `201 Created` / `204 No Content`
- `400 Bad Request` / `401 Unauthorized` / `403 Forbidden`
- `404 Not Found` / `409 Conflict` / `500 Internal Server Error`

### Response Format

```typescript
// Single resource
{ "data": {...}, "meta": {...} }

// List with pagination
{ "data": [...], "pagination": { "page", "limit", "total" } }
```

### Error Format

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

## Best Practices

- Consistent naming conventions
- Validate all inputs with DTOs
- OpenAPI/Swagger documentation
- Authentication on all endpoints
- Pagination for lists
- Version APIs from the start

---

**For complete DTO examples, pagination/filtering/sorting patterns, versioning strategies, OpenAPI setup, CRUD controller patterns, nested resources, bulk operations, and anti-patterns, see:** `references/full-guide.md`
