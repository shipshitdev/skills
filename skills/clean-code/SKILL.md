---
name: clean-code
description: Improve readability, cohesion, naming, and maintainability without changing behavior. Use when refactoring messy code, simplifying modules, reducing duplication, or preparing code for review.
metadata:
  version: "1.0.0"
  tags: "code-quality, refactoring, maintainability"
---

# Clean Code

Refactor code to be easier to understand, change, and review without introducing behavioral drift.

## Use This Skill For

- Overgrown functions or classes
- Vague naming and mixed responsibilities
- Duplicate logic or inconsistent patterns
- Dead abstractions, dead code, or misleading comments
- Pre-review cleanup when the code works but is hard to maintain

## Workflow

### 1. Lock Behavior First

- Read existing tests before editing
- If behavior is unclear, derive it from current callers and runtime paths
- Preserve public contracts unless the user explicitly asked for API changes

### 2. Study Local Patterns

- Find at least 3 similar modules in the codebase
- Match naming, error handling, file structure, and test style
- Reuse existing helpers before introducing new abstractions

### 3. Refactor for Clarity

Prioritize, in order:

1. Better names
2. Smaller focused functions
3. Clearer control flow
4. Removing duplication
5. Removing dead code and misleading comments
6. Narrowing types and interfaces

### 4. Avoid Over-Engineering

- Do not introduce patterns just because they are fashionable
- Prefer straightforward code over clever indirection
- Extract abstractions only when they reduce real duplication or confusion

### 5. Verify

- Run the narrowest relevant tests first
- Run linting or type checks if the project uses them
- Confirm behavior and external interfaces are unchanged

## Heuristics

- One function should do one job
- Names should explain intent, not implementation trivia
- Comments should explain why, not restate what the code already says
- Conditionals should read top-to-bottom without mental backtracking
- Shared logic belongs in one place, but not at the cost of unreadable abstractions

## Red Flags

- Generic names like `data`, `item`, `temp`, `helper`, `util`
- Boolean parameters that change function meaning
- Functions that both fetch, transform, and render
- Duplicate validation or mapping logic
- Commented-out code or TODOs masking uncertainty

## Output

When using this skill, produce:

- The code changes
- A short explanation of what was simplified
- Any residual risk if behavior was inferred rather than explicitly tested
