---
name: ai-regression-testing
description: Design regression tests for AI-assisted development by targeting model blind spots such as sandbox versus production path drift, response-shape mismatches, untested bug fixes, and same-model review failures. Use after AI-generated code changes, bug fixes, API edits, or feature-flag/sandbox changes.
metadata:
  version: "2.2.2"
  tags: "testing, ai, regression, quality, api"
---

# AI Regression Testing

Add tests that catch the failures AI agents commonly miss when the same model
writes code and reviews its own assumptions.

## Contract

Inputs:

- Bug report, code diff, API change, route, component, feature flag, or sandbox path
- Existing test commands and project conventions
- Optional known production incident or regression id

Outputs:

- Regression test plan
- New or updated tests when implementation is requested
- Parity checklist for sandbox, mock, feature-flag, and production paths
- Verification commands and results

Creates/Modifies:

- Test files, fixtures, mocks, and minimal helpers when asked to implement
- Application code only when the user also asks to fix the failing behavior

External Side Effects:

- None by default
- Do not hit production services; use sandbox, fixtures, local test databases, or mocked providers

Confirmation Required:

- Before changing production data, external accounts, CI settings, or destructive test fixtures

Delegates To:

- `testing-expert` for general testing strategy
- `react-testing-library` for React component tests
- `playwright-e2e-init` for browser setup or `test-runner` for existing browser tests
- `debug` when the root cause is still unknown

## When to Use

- AI modified API routes, backend logic, serializers, or response schemas.
- A bug was fixed and must not reappear.
- A feature has sandbox/mock and production paths.
- A model-generated review says the change is correct but no test proves it.
- Build and lint pass, but the user-facing contract may still be wrong.
- A feature flag, mock mode, fallback path, or error path was changed.

## Core Principle

Test the contract that failed, not the implementation the agent wrote. Assume the reviewing model shares the same blind spot as the writing model.

Common AI blind spots:

- production path fixed but sandbox/mock path still wrong
- response includes a field in one path but not another
- `SELECT`, serializer, DTO, fixture, and frontend type drift apart
- optimistic UI path works but rollback/error path is untested
- feature flag changes one branch but not the fallback branch
- tests assert status codes but not response shape or state transition

## Workflow

### 1. Identify the Contract

State the behavior as a user or caller contract:

- endpoint returns these fields
- component shows this state after this interaction
- webhook processes duplicate events idempotently
- sandbox and production return the same shape
- failed operation rolls back visible and persisted state

Create a required-field or required-state list when useful.

### 2. Find All Paths

Trace every path that should satisfy the contract:

- production data path
- sandbox/mock/demo path
- feature-flag on/off path
- authenticated/unauthenticated path
- success, validation error, provider error, and retry path
- server response, client type, and UI rendering path

### 3. Write the Regression First

The first test should fail on the unfixed bug or on a representative broken
fixture. If the bug is already fixed, make the test specific enough that the
previous bug would have failed.

Prefer deterministic checks:

- unit or route handler tests for response shape
- integration tests for database, serializer, and service contracts
- component tests for state transitions
- E2E tests only for critical user journeys or cross-system behavior

### 4. Test Parity

For API and data contracts, compare path shapes:

```text
production fields == sandbox fields == mock fixture fields
frontend type accepts exactly the returned shape
empty/error states still include documented envelope fields
```

Use fixtures with realistic nulls, missing optional values, and date formats.

### 5. Verify

Run the narrow test first, then the relevant suite:

```bash
bun test path/to/regression.test.ts
bun test
bun run typecheck
```

Use the repo's actual package manager and test commands. Do not invent new
tooling when the project already has a pattern.

## Test Design Checklist

- Does the test fail for the old bug?
- Does it cover every branch that returns or mutates the contract?
- Does it assert the actual response/body/state, not only `200 OK`?
- Does it include sandbox/mock parity when those modes exist?
- Does it cover null, empty, duplicate, retry, and provider-failure cases when relevant?
- Is the test small enough to run in a bug-check loop?
- Is the regression named after the bug or contract it protects?

## Output Format

```markdown
Regression target: `GET /api/profile` must include `notification_settings` in production and sandbox responses.

Tests added:
- `tests/api/profile.test.ts`: response-shape contract
- `tests/api/profile.test.ts`: sandbox/production field parity

Verification:
- `bun test tests/api/profile.test.ts` passed
- `bun run typecheck` passed

Residual risk:
- No E2E coverage for the settings page rendering this field.
```

## Anti-Patterns

- Letting an AI review replace a mechanical test.
- Testing only the path the fix touched.
- Asserting vague success instead of the exact contract.
- Using production systems for regression tests.
- Adding broad flaky E2E coverage when a route or unit test catches the bug.
- Forgetting fixtures and generated types after changing response shape.
