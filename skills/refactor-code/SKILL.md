---
name: refactor-code
description: Systematic approach to safely refactoring code with tests. Use when user says 'refactor', 'clean up code', 'simplify', 'reduce complexity', or 'technical debt'.
metadata:
  version: 1.0.0
  tags: refactoring, code-quality, testing, maintenance
---

# Refactor Code

Systematic approach to refactoring code safely.

## Triggers

- Function > 50 lines
- File > 300 lines
- Duplicate code (3+ instances)
- Complex conditionals (> 3 levels deep)
- `any` types
- Hard to test or understand

## Steps

### 1. Write Tests First

Test current behavior comprehensively before changing anything.

### 2. Check Examples

Find 3+ similar implementations in the codebase to follow.

### 3. Make Small Changes

Refactor incrementally — one change at a time:

- **Extract Function**: Break long methods into focused helpers
- **Extract Constants**: Replace magic numbers/strings
- **Replace `any`**: Define proper TypeScript interfaces
- **Extract Service**: Move business logic out of controllers
- **Extract Component**: Split large React components

### 4. Run Tests After Each Change

```bash
npm test -- [specific-test-file]
```

### 5. Refactoring Checklist

Before starting:

- [ ] All tests passing
- [ ] Understand what the code does
- [ ] Have example pattern to follow
- [ ] Committed current working code

During:

- [ ] One change at a time
- [ ] Tests after each change
- [ ] Same public API
- [ ] Document why (not just what)

After:

- [ ] All tests still passing
- [ ] No behavior changes
- [ ] Code is more readable
- [ ] Performance same or better

## Red Flags (Stop and Reconsider)

- Behavior changes during refactoring
- Tests start failing
- Need to change public API
- Unclear what code does
- No test coverage to verify

## Safe Refactoring Rules

1. Always have tests first
2. One change at a time
3. Run tests after each change
4. Keep same behavior
5. Don't change public API
6. Commit working states
