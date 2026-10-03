---
name: code-review
description: Reviews a PR or diff for correctness, security, and spec fidelity, including TypeScript, database safety, tests, and flag leaks. Use for /code-review or is this safe to merge.
metadata:
  version: "2.2.2"
  tags: "code-review, correctness, security, testing, devex, feature-flags, spec"
  author: Ship Shit Dev
allowed-tools: Bash(git *) Bash(gh *)
when_to_use: "check the diff, review my code"
---

# Code Review

Correctness and security gate. High-conviction findings only — flag issues you
are certain about. Ambiguity defaults to "request changes." Structural concerns
(cohesion, abstraction altitude, circular deps, dead code) belong to the
`structural-review` skill; trust it on those axes and own correctness + security
here.

Stack rules from the repo's agent instruction file (Bun, Tailwind v4, Next.js 16,
shadcn/ui) are validated by the correctness review harness's rule-compliance
layer. Do not re-flag them here.

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

- `structural-review` for cohesion/abstraction/dead-code axes.
- `security-audit` for OWASP-depth security review.
- `codebase-design` when a finding is about module depth or seam placement.

## Spec Axis

The checklist below is the **Standards** axis (correctness + security + this
repo's hygiene). Run a **Spec** axis in parallel so a change that follows every
standard but implements the wrong thing cannot hide, and a change that matches
the issue but breaks conventions cannot hide.

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → Standards
  pass, Spec fail.
- Code that does exactly what the issue asked but breaks project conventions →
  Spec pass, Standards fail.

Report them under `## Standards` and `## Spec`. Do not merge or rerank findings
across axes.

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag,
`main`, `HEAD~5`. If they did not specify one, ask. Confirm it resolves and the
diff is non-empty (`git diff <fixed-point>...HEAD`) before reviewing.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in commit messages (`#123`, `Closes #45`) — fetch via `gh`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or the issue body matching the branch.
4. If nothing is found, ask. If there is no spec, skip the Spec axis and report
   "no spec available".

### 3. Spec findings

Report:

- Requirements the spec asked for that are missing or partial
- Behaviour in the diff that was not asked for (scope creep)
- Requirements that look implemented but where the implementation looks wrong

Quote the spec line for each finding. Spec misses that drop required behaviour
are Block Merge. Scope creep is Request Changes unless the user already accepted
it.

## Critical Checklist

### 1. Security and Data Isolation

- ALL queries filter by tenant/organization (if multi-tenant)
- ALL queries filter soft-deleted records (if applicable)
- No cross-tenant data access
- Auth guards on protected routes
- No unintended public endpoints — every route's auth posture is intentional
- Input validation via DTOs/schemas
- No secrets, tokens, or credentials committed or logged

### 2. TypeScript

- No `any` types — define proper interfaces or named types in `*.types.ts`
- No bare `unknown` without a type guard — bare `unknown` is deferred `any`
- No `as X` casts without an explanatory comment
- Interfaces/props in dedicated files, not inline in component or service files
- Return types on all functions
- No `console.log` — use the project logger (LoggerService, pino, winston)
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
- Sequential `await db.update()` calls that can leave the DB half-written on
  failure must be wrapped in a transaction or collapsed to a single atomic write

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
- API documentation decorators present where the project uses them (e.g.
  `@ApiOperation` / `@ApiResponse`)
- No internal stack traces leaked to API consumers

### 9. Devex Regressions

Changes that silently break the local dev loop for other engineers:

- **Env var renames or additions** — is there a corresponding update to
  `.env.example` / `.env.template`? Is the rename announced (migration note,
  changelog, or PR description)?
- **Secret-read changes** — new secrets accessed at runtime that are not in the
  documented setup path; access moved from one provider/vault path to another
  without updating the runbook
- **Port or network remaps** — service, dev-server, or docker-compose port
  changed without updating README/setup docs and all dependent config files
- **New mandatory setup scripts** — a migration, seed, or one-time bootstrap
  that must be run before the app starts; not documented in the PR description
  or setup guide
- **Build-flow changes** — new required build steps, changed output directories,
  added pre/post scripts in `package.json` that break the existing
  `bun run dev` / `bun run build` contract without a clear migration note

Block merge when a devex regression is unannounced. Request changes when it is
documented but the documentation is in the wrong place.

### 10. Feature-Flag / Gate Leaks

Features meant to be gated that are shipping unflagged or partially flagged:

- **Obvious leaks** — a new route, component, or API endpoint that the PR
  description says is behind a flag, but the flag check is absent or only
  applied to the UI, not the API handler
- **Subtle leaks** — flag check present in the happy path but absent in an
  error handler, a background job, or an admin-only path that calls the same
  service method
- **Always-on constants** — `const ENABLE_NEW_CHECKOUT = true` standing in for
  a real flag evaluation; will never be cleaned up and bypasses the flag service
- **Flag introduced without a cleanup plan** — no linked issue or TODO comment
  for flag removal; flag names should make the intended lifetime obvious
- **Rollout config inconsistencies** — flag defined in the PR but the rollout
  percentage / targeting rule is missing or set to 100% default, defeating the
  purpose of gating

Flag leaks that expose unreleased functionality to all users are merge blockers.
Missing cleanup tickets are a "request changes."

## Approval Criteria

### Block Merge

- Security issues present
- Missing tenant/organization filtering (if required)
- `any` types or bare `unknown` without type guards
- Tests failing or tests entirely absent for new public methods
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
- Feature flags have cleanup plan
- Spec axis passes, or was skipped because no spec exists

## Scope Boundary

This skill = **correctness + security gate**.

Use it for an individual diff or PR. Route a report-only multi-PR request such as
"review all PRs" through `review-dispatch`, which applies this gate per PR. The
only non-serial queue-drain mode is exact `/merge force`, owned by
`merge-open-prs`; never infer that mutating mode from a review request.

Structural and maintainability concerns — module cohesion, abstraction altitude,
circular dependencies, dead-code introduction, API surface sprawl, whether the
implementation matches the stated architecture — belong to the `structural-review`
skill. Do not re-litigate those axes here; trust `structural-review` to own them.

Security-audit depth (OWASP rubric, dependency CVEs, timing attacks, privilege
escalation paths) belongs to the `security-audit` skill. Surface obvious issues
found in the diff, but do not attempt a full security audit in this skill.
