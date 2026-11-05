# Performances Protocol

Shared rules for every `/performances` action. Read this with the action's
playbook. Where they differ, the playbook wins.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Edit only the target repository, within the scope the
user named (default: the whole repository). Keep report-only requests
report-only, honor the caller's target, host, provider, and cost limits, ask
before expanding scope, and forward these limits to delegates.

Never run load, migrations, or write traffic against production or any shared
environment, never read production secrets, and never deploy. Stop and ask
before anything that cannot be undone.

## Contract

Inputs:

- Optional scope: a path, module, endpoint, or table
- The target repository checkout (current directory)

Outputs:

- A stack profile, including what does not apply
- A before/after evidence table (and chart where the action produces one)
- One PR per action that changed code, or a no-op report

Creates/Modifies:

- Source, tests, and config in the target repository, on a branch per action
- Scratch files in the repository's `.tmp/`, never `/tmp`

External Side Effects:

- Pushes a branch and opens a PR per action
- Reads the web where the playbook names a source

Confirmation Required:

- Before adding a new vendor, service, or dependency that changes cost or data flow
- Before any production migration, backfill, or deploy (never performed here)
- Before running a suite against anything but a throwaway local database
- Before expanding beyond the requested scope

Delegates To:

- `/git pr` playbook (`git/references/pr.md`) when installed, else `gh`
- `/git worktree` playbook (`git/references/worktree.md`) when installed, else `git worktree`
- Read the installed playbook and follow it; never assume this repository is checked out

## 1. Detect the stack

Before touching code, build a stack profile from manifests, lockfiles, config,
and imports. Record:

- Language and runtime, framework, package manager, test runner, CI, lint setup
- ORM or query layer, database engine and version, migration tool
- Observability vendor and SDKs, logger, error tracker
- Deployment shape that affects measurement (serverless, long-lived server,
  workers, edge)

Print the profile, then a **Does not apply** list: every part of the playbook
the stack makes moot, with the reason. If the action does not apply at all,
report that and stop; open no PR. Adapt every idiom in the playbook to the
detected stack. The playbooks use JavaScript, SQL, and Postgres as examples
only.

## 2. Measure before, fix, measure after

1. Choose the metric the change can move: latency, query count, bytes
   transferred, allocations, CPU, span or log volume, or overhead budget.
2. Capture the baseline before editing, on the same machine, data, and load you
   will use after. Warm up first. Take at least 20 samples per scenario
   (`compare.py` refuses to judge fewer than 5). Record the environment: commit,
   runtime version, hardware, dataset size, concurrency.
3. Make the change.
4. Capture the same scenarios again with the same procedure. Alternate the
   variants in blocks when both can run in one harness, so drift hits both.
5. Compare with `scripts/compare.py` from the installed skill directory. Report
   the median change, its 95% interval, the adjusted p-value, and the verdict.
   Claim an improvement only when the verdict says `improved`. Report
   `no significant change` and `regressed` results as they are.
6. A change with no measurable effect is dropped from the PR unless it is a
   zero-risk structural fix the playbook names; say which, and why, in the PR.
   Actions whose purpose is capability, not speed (`otel`, `logging`), measure
   an overhead budget and coverage instead of a speedup.

Profile before guessing. Rank candidates by frequency on hot paths times cost
per call, using traces, APM, slow query logs, or a profiler when the project has
them, and by reading the code when it does not. Say which you used.

## 3. Preserve behavior

- Tests first: if code you will change lacks coverage of its observable
  behavior (results, ordering, errors, status codes, side effects), add
  characterization tests that pass on the unchanged code, then change the code.
- The whole existing suite passes before and after.
- Do not change public APIs, response shapes, ordering guarantees, error types
  or messages, retry semantics, or the order of externally visible side effects.
- When a candidate would change behavior, leave it alone and list it under
  **Not changed** with the reason.
- Keep each PR to what the action needs. No drive-by refactors.

## 4. One PR per action

- Branch `perf/<action>` from freshly fetched `origin/<default>`. Use a separate
  worktree per action when running several.
- Conventional commits: `perf:` for speed changes, `feat:` for new capability
  (`otel`, `logging`, `dbload`), `test:` for tests-only commits.
- Run the project's own lint, typecheck, and tests before pushing.
- The PR body, following the repository's PR template when it has one:
  1. Stack profile and Does not apply
  2. Findings, ranked, with how each was measured
  3. Changes, by file
  4. Evidence: before/after table from `compare.py`, chart attached or linked
  5. Behavior preservation: tests added, suites run
  6. Not changed, and why
  7. Risk and rollback
  8. Approvals needed, if any (production migration, new vendor)
- Never merge, never deploy, never close another PR. Recommend `/git babysit`
  for the follow-through.
- No changes means no PR: report the no-op instead.

## 5. Final report

One short report per action: result first, then the PR link, the headline
before/after numbers, what does not apply, what was left unchanged, and what the
user must approve or decide.

## 6. Safety rules for anything that connects to a database

- Use a throwaway database the run creates and drops itself. Verify the host is
  local or ephemeral and the database name carries a run marker before the first
  statement. Refuse otherwise.
- Never use a `DATABASE_URL` from the environment without that check. Never read
  production env files.
- Seed data is synthetic. Do not copy production rows.
- Teardown on success and on failure.
