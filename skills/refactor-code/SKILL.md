---
name: refactor-code
description: Refactors code safely behind tests without changing behavior. Use when asked to refactor, clean up, simplify, reduce complexity, or pay down technical debt in specific code.
metadata:
  version: "2.2.4"
  tags: "refactoring, code-quality, testing, maintenance, clean-code"
when_to_use: "long function, duplicate code, mixed responsibilities"
---

# Refactor Code

Improve readability, cohesion and maintainability without changing behavior.

Related skills, if available: a TypeScript skill for type-architecture work, `react-refactor` for component architecture, a de-slop skill for mechanical AI-slop removal, a structural-review skill for a read-only review.

## Triggers

- Function > 50 lines; file > 300 lines
- Duplicate code (3+ instances)
- Conditionals nested > 3 levels
- `any` types
- Hard to test or understand; vague naming; mixed responsibilities
- Dead abstractions, dead code or misleading comments

## Steps

### 1. Lock behavior first

- Read existing tests before editing.
- If behavior is unclear, derive it from current callers and runtime paths.
- Preserve public contracts unless an API change was requested.

### 2. Study local patterns

Find 3+ similar implementations in the codebase. Match naming, error handling, file structure and test style. Reuse existing helpers before introducing new abstractions.

### 3. Refactor for clarity

Small, incremental changes, one at a time, in this priority order:

1. Better names
2. Smaller focused functions (extract long methods into helpers)
3. Clearer control flow
4. Removing duplication
5. Removing dead code and misleading comments
6. Narrowing types and interfaces (replace `any` with proper types)
7. Extracting constants (replace magic numbers/strings)
8. Extracting a service/component (move business logic out of controllers, split large components)

### 4. Avoid over-engineering

- Do not introduce patterns because they are fashionable.
- Prefer straightforward code over clever indirection.
- Extract abstractions only when they reduce real duplication or confusion.

### 5. Run tests after each change

```bash
bun run test <specific-test-file>
```

Use the project's own test command if it differs.

## Heuristics

- One function does one job.
- Names explain intent, not implementation trivia.
- Comments explain why, not what.
- Conditionals read top-to-bottom without backtracking.
- Shared logic lives in one place, but not at the cost of unreadable abstractions.

## Red flags (stop and reconsider)

- Generic names like `data`, `item`, `temp`, `helper`, `util`
- Boolean parameters that change function meaning
- Functions that fetch, transform and render
- Duplicate validation or mapping logic
- Commented-out code or TODOs masking uncertainty
- Behavior changes during refactoring
- Tests start failing
- Need to change the public API
- Unclear what the code does

## Checklist

Before: all tests passing; the code is understood; an example pattern to follow exists; current working code is committed.

During: one change at a time; tests after each change; same public API; document why, not just what.

After: all tests still passing; no behavior changes; code is more readable; performance same or better.
