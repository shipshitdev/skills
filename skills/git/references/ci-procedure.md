## Distribution boundary

Run other skills from their playbooks under the installed skills directory and use the caller's existing authorization.
The harness owns host, account, model, effort, sandbox, worktree and schedule.
Upstream examples describe mechanisms; they do not grant permission or select
providers. Preserve report-only scope. External messages, publication, installs,
deployment and destructive actions require authorization covering that action.
Read configuration from the harness source of truth; never replace its role map
with an example here. Use only capabilities the active harness actually exposes.

# Fix CI

## Trigger

Branch or PR CI is failing and needs a fast, iterative path to green checks.

## Workflow

1. Resolve the active PR and inspect `gh pr checks --json name,bucket,state,workflow,link`.
2. Inspect failed jobs and extract the first actionable error. Use GitHub Actions logs when available; otherwise use the check link to identify the failing command or service.
3. Apply the smallest safe fix.
4. Push, re-check the PR check set, and repeat until green.

## Guardrails

- Fix one actionable failure at a time.
- Prefer minimal, low-risk changes before broader refactors.
- Keep `gh pr checks` as the source of truth for overall PR CI state.

## Output

- Primary failing job and root error
- Fixes applied in iteration order
- Current CI status and next action
