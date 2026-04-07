---
name: code-review
description: Comprehensive code review focusing on quality, security, performance, and testing. Use when user says 'review', 'code review', 'check my code', or before merging PRs.
version: 1.0.0
tags:
  - code-review
  - quality
  - security
  - testing
  - best-practices
---

# Code Review

Comprehensive code review focusing on quality, security, performance, and testing.

## Quick Review

```bash
git status
git diff HEAD~1
git log --oneline -5
git branch --show-current
```

## Critical Checklist

### 1. Security and Data Isolation

- ALL queries filter by tenant/organization (if multi-tenant)
- ALL queries filter soft-deleted records (if applicable)
- No cross-tenant data access
- Auth guards on protected routes
- Input validation via DTOs/schemas

### 2. TypeScript

- No `any` types — define proper interfaces
- Interfaces/props in dedicated files, not inline
- Return types on all functions
- No `console.log` — use project logger

### 3. Pattern Compliance

- Follows existing codebase patterns (check 3+ similar implementations)
- Path aliases over relative imports
- Consistent with project conventions

### 4. Database

- Tenant/organization filter in ALL queries (if applicable)
- Soft delete filter in ALL queries (if applicable)
- Projections for large documents
- Indexes exist for query patterns
- No N+1 queries

### 5. Error Handling

- Try/catch blocks present
- Framework-specific exceptions (not generic Error)
- Errors logged via logger service
- Generic messages to client (no internals exposed)

### 6. Testing

- Unit tests exist and pass
- All public methods tested
- Error cases tested
- Coverage > 70% for new code

### 7. Frontend

- Cleanup in useEffect with async calls (AbortController)
- Loading and error states handled
- Semantic HTML with ARIA labels

### 8. API

- API documentation decorators present
- Proper HTTP status codes
- DTOs for request/response

## Approval Criteria

### Block Merge

- Security issues present
- Missing tenant/organization filtering (if required)
- `any` types used
- Tests failing
- Build failing

### Request Changes

- Coverage < 70%
- Missing documentation
- Performance concerns
- Pattern violations

### Approve

- All security checks pass
- Tests passing with good coverage
- Follows codebase patterns
