---
name: code-review
description: Reviews a PR or diff for correctness, security, and spec fidelity, including TypeScript, database safety, tests, and flag leaks. Use for /code-review or is this safe to merge.
metadata:
  tags: "code-review, correctness, security, testing, devex, feature-flags, spec"
  author: Ship Shit Dev
allowed-tools: Bash(git *) Bash(gh *)
when_to_use: "check the diff, review my code"
disable-model-invocation: true
---

# Code Review

Correctness and security gate. Report only high-conviction findings: flag issues you are certain about. Ambiguity defaults to "request changes". Structural concerns (cohesion, abstraction altitude, circular dependencies, dead code) belong to a structural review; own correctness and security here.

If the repo has automated rule-compliance checks for its stack rules (package manager, CSS framework, framework version, UI library), do not re-flag what they already cover.

## Scope

- **Input:** one diff, branch, or PR. Gather scope with read-only `git` and `gh` commands.
- **Output:** a findings list bucketed into Block Merge / Request Changes / Approve, each with file, line, and a one-sentence rationale, plus a separate **Spec** report.
- **Read-only:** this skill reports. It does not edit files, open PRs, mutate anything, or deploy. All output is advisory; no confirmation is needed.
- **Boundaries:** for an individual diff or PR only. Do not re-litigate structural axes (module cohesion, abstraction altitude, circular dependencies, dead-code introduction, API surface sprawl, architecture fit); hand those to a structural review. Surface obvious security issues in the diff but do not attempt a full audit (OWASP rubric, dependency CVEs, timing attacks, privilege escalation paths); hand that to a dedicated security audit. If a finding is about module depth or seam placement, recommend a codebase-design review. Never infer a merge or queue-drain action from a review request.

## Two axes

The checklist below is the **Standards** axis (correctness, security, repo hygiene). Run a **Spec** axis alongside it so a change that follows every standard but implements the wrong thing cannot hide, and a change that matches the issue but breaks conventions cannot hide.

- Follows every standard but implements the wrong thing: Standards pass, Spec fail.
- Does exactly what the issue asked but breaks project conventions: Spec pass, Standards fail.

Report them under `## Standards` and `## Spec`. Do not merge or rerank findings across axes.

### Spec axis steps

1. **Pin the fixed point.** Whatever the user named is the fixed point: a commit SHA, branch, tag, `main`, `HEAD~5`. If none was given, ask. Confirm it resolves and the diff is non-empty (`git diff <fixed-point>...HEAD`) before reviewing.
2. **Identify the spec source**, in this order:
   1. Issue references in commit messages (`#123`, `Closes #45`), fetched via `gh`.
   2. A path the user passed as an argument.
   3. A spec file under `docs/`, `specs/`, or the issue body matching the branch.
   4. If nothing is found, ask. If there is no spec, skip the Spec axis and report "no spec available".
3. **Report spec findings:**
   - Requirements the spec asked for that are missing or partial
   - Behaviour in the diff that was not asked for (scope creep)
   - Requirements that look implemented but where the implementation looks wrong

   Quote the spec line for each finding. Spec misses that drop required behaviour are Block Merge. Scope creep is Request Changes unless the user already accepted it.

## Critical Checklist (Standards axis)

### 1. Security and Data Isolation

- ALL queries filter by tenant/organization (if multi-tenant)
- ALL queries filter soft-deleted records (if applicable)
- No cross-tenant data access
- Auth guards on protected routes
- No unintended public endpoints: every route's auth posture is intentional
- Input validation via DTOs/schemas
- No secrets, tokens, or credentials committed or logged

### 2. TypeScript

- No `any` types: define proper interfaces or named types in `*.types.ts`
- No bare `unknown` without a type guard (bare `unknown` is deferred `any`)
- No `as X` casts without an explanatory comment
- Interfaces/props in dedicated files, not inline in component or service files
- Return types on all functions
- No `console.log`: use the project logger (LoggerService, pino, winston)
- No `@ts-ignore` or `@ts-expect-error` without an explanatory comment

### 3. Pattern Compliance

- Follows existing codebase patterns (verify 3+ real examples before flagging)
- Path aliases over relative imports

### 4. Database

- Tenant/organization filter in ALL queries (if applicable)
- Soft delete filter in ALL queries (if applicable)
- Projections for large documents
- Indexes exist for query patterns
- No N+1 queries visible in the diff
- Sequential `await db.update()` calls that can leave the DB half-written on failure must be wrapped in a transaction or collapsed to a single atomic write

### 5. Error Handling

- Try/catch blocks present
- Framework-specific exceptions (not generic `Error`)
- Errors logged via logger service
- Generic messages to client (no internals exposed)

### 6. Testing

- Unit tests exist and pass
- All public methods tested
- Error cases tested
- Tests assert behavior, not just that code runs (no hollow snapshot tests)

### 7. Frontend

- Cleanup in `useEffect` with async calls (`AbortController`)
- Loading and error states handled
- Semantic HTML with ARIA labels where interactive elements are added

### 8. API

- Proper HTTP status codes
- DTOs for request/response
- API documentation decorators present where the project uses them (e.g. `@ApiOperation` / `@ApiResponse`)
- No internal stack traces leaked to API consumers

### 9. Devex Regressions

Changes that silently break the local dev loop for other engineers:

- **Env var renames or additions:** is `.env.example` / `.env.template` updated? Is the rename announced (migration note, changelog, or PR description)?
- **Secret-read changes:** new secrets accessed at runtime that are not in the documented setup path, or access moved from one provider/vault path to another without updating the runbook
- **Port or network remaps:** service, dev-server, or docker-compose port changed without updating README/setup docs and all dependent config files
- **New mandatory setup scripts:** a migration, seed, or one-time bootstrap that must run before the app starts and is not documented in the PR description or setup guide
- **Build-flow changes:** new required build steps, changed output directories, or added pre/post scripts in `package.json` that break the existing dev/build contract without a clear migration note

Block merge when a devex regression is unannounced. Request changes when it is documented but the documentation is in the wrong place.

### 10. Feature-Flag / Gate Leaks

Features meant to be gated that ship unflagged or partially flagged:

- **Obvious leaks:** a new route, component, or API endpoint that the PR description says is behind a flag, but the flag check is absent or applied only to the UI, not the API handler
- **Subtle leaks:** flag check present in the happy path but absent in an error handler, a background job, or an admin-only path that calls the same service method
- **Always-on constants:** `const ENABLE_NEW_CHECKOUT = true` standing in for a real flag evaluation; it will never be cleaned up and bypasses the flag service
- **Flag introduced without a cleanup plan:** no linked issue or TODO comment for flag removal; flag names should make the intended lifetime obvious
- **Rollout config inconsistencies:** flag defined in the PR but rollout percentage / targeting rule is missing or defaults to 100%, defeating the purpose of gating

Flag leaks that expose unreleased functionality to all users are merge blockers. Missing cleanup tickets are "request changes".

## Approval Criteria

### Block Merge

- Security issues present
- Missing tenant/organization filtering (if required)
- `any` types or bare `unknown` without type guards
- Tests failing, or tests entirely absent for new public methods
- Build failing
- Feature-flag leak exposing unreleased functionality
- Unannounced devex regression (broken env, port, or build contract)
- Non-atomic multi-step DB mutations with no transaction

### Request Changes

- Missing documentation for env var additions or setup-script requirements
- Performance concerns clearly visible in the diff (N+1, missing index)
- Pattern violations (raw HTML in files that already import the UI library)
- Feature flag introduced without a cleanup issue/TODO
- Hollow tests that assert execution rather than behavior

### Approve

- All security checks pass
- Tests pass and assert real behavior
- Follows codebase patterns
- Devex impact documented
- Feature flags have a cleanup plan
- Spec axis passes, or was skipped because no spec exists

## Contract

Inputs:

- A single diff, branch, or PR to review. Read-only `git`/`gh` commands gather
  scope.

Outputs:

- A findings list bucketed into Block Merge / Request Changes / Approve, each
  with file, line, and a one-sentence rationale.
- A **Spec** report alongside the checklist: missing requirements, scope creep,
  and wrong implementations relative to the originating issue. Keep the two axes
  separate so one cannot mask the other.

Creates/Modifies:

- None. This skill reports; it does not edit files or open PRs.

External Side Effects:

- Read-only `git` and `gh` invocations only. No mutations, no deploys.

Confirmation Required:

- None. All output is advisory.

Delegates To:

- None. Recommend a structural, security, or codebase-design review (for example the
  upstream pstack workflows, when installed) for findings outside this gate.
