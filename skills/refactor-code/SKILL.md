---
name: refactor-code
description: Refactors code safely behind tests without changing behavior. Use when asked to refactor, clean up, simplify, reduce complexity, or pay down technical debt in specific code.
metadata:
  version: "2.2.4"
  tags: "refactoring, code-quality, testing, maintenance, clean-code"
when_to_use: "long function, duplicate code, mixed responsibilities"
---

# Refactor Code

Improve readability, cohesion, and maintainability without changing behavior.

The `code` engine of the refactoring vertical (`/refactor code`). Draws on
`typescript-expert` (its `references/rules/` library) for type-architecture work and `react-refactor` for component
architecture. For mechanical AI-slop removal use `deslop`; for a read-only structural
review use `structural-review`.

## Triggers

- Function > 50 lines
- File > 300 lines
- Duplicate code (3+ instances)
- Complex conditionals (> 3 levels deep)
- `any` types
- Hard to test or understand
- Vague naming and mixed responsibilities
- Dead abstractions, dead code, or misleading comments

## Steps

### 1. Lock Behavior First

- Read existing tests before editing
- If behavior is unclear, derive it from current callers and runtime paths
- Preserve public contracts unless explicitly asked for API changes

### 2. Study Local Patterns

Find 3+ similar implementations in the codebase. Match naming, error handling, file structure, and test style. Reuse existing helpers before introducing new abstractions.

### 3. Refactor for Clarity

Small, incremental changes — one at a time. Prioritize in order:

1. Better names
2. Smaller focused functions (extract long methods into helpers)
3. Clearer control flow
4. Removing duplication
5. Removing dead code and misleading comments
6. Narrowing types and interfaces (replace `any` with proper types)
7. Extract constants (replace magic numbers/strings)
8. Extract service/component (move business logic out of controllers, split large components)

### 4. Avoid Over-Engineering

- Don't introduce patterns just because they're fashionable
- Prefer straightforward code over clever indirection
- Extract abstractions only when they reduce real duplication or confusion

### 5. Run Tests After Each Change

```bash
bun run test <specific-test-file>
```

## Heuristics

- One function should do one job
- Names should explain intent, not implementation trivia
- Comments should explain why, not restate what the code already says
- Conditionals should read top-to-bottom without mental backtracking
- Shared logic belongs in one place, but not at the cost of unreadable abstractions

## Red Flags (Stop and Reconsider)

- Generic names like `data`, `item`, `temp`, `helper`, `util`
- Boolean parameters that change function meaning
- Functions that both fetch, transform, and render
- Duplicate validation or mapping logic
- Commented-out code or TODOs masking uncertainty
- Behavior changes during refactoring
- Tests start failing
- Need to change public API
- Unclear what code does

## Checklist

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
