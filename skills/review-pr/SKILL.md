---
name: review-pr
description: Systematic PR review checklist for quality, security, and consistency. Use when user says 'review PR', 'check PR', 'PR review', or before merging a pull request.
version: 1.0.0
tags:
  - pull-request
  - code-review
  - quality
  - security
---

# Review PR

Systematic code review for quality, security, and consistency before merging.

## Review Checklist

### 1. TypeScript

- No `any` types
- Interfaces/types in dedicated files
- Return types on functions
- No `console.log` — use logger service

### 2. Security and Data Isolation

- ALL queries filter by tenant/organization (if multi-tenant)
- ALL queries filter soft-deleted records (if applicable)
- No cross-tenant data leaks
- DTOs with validation decorators
- ID validation present

### 3. Authentication

- Auth guards applied to protected routes
- User context decorator used correctly
- No unintended public endpoints

### 4. Database

- Tenant/organization filter in ALL queries (if applicable)
- Soft delete filter in ALL queries (if applicable)
- Projections for large documents
- Indexes for query patterns
- No N+1 queries

### 5. Error Handling

- Try/catch blocks present
- Framework-specific exceptions used
- Errors logged with logger service
- No internals exposed to client

### 6. Testing

- Unit tests written and passing
- Error cases tested
- Coverage > 70% for new code

### 7. Frontend

- Props in dedicated files
- Loading and error states handled
- Accessibility (aria labels, keyboard nav)

### 8. API

- API documentation decorators present
- Proper HTTP status codes
- DTOs for request/response

### 9. Performance

- No unnecessary re-renders (React)
- Database queries optimized
- No blocking operations in API

### 10. Best Practices

- Follows SOLID principles
- DRY (Don't Repeat Yourself)
- Code is self-documenting
- Functions < 50 lines, Files < 300 lines

## Approval Criteria

**Block Merge**: Security issues, missing tenant filtering, `any` types, failing tests/build
**Request Changes**: Low coverage, missing docs, performance concerns
**Approve**: All security checks pass, tests passing, follows patterns
