---
name: github-inbox
description: Triages a GitHub work inbox of assigned issues, review requests, mentions, and authored PRs with failing checks. Use when checking what needs attention or prioritizing tasks.
compatibility: Requires GitHub CLI gh access. The bundled inbox report script runs with Node.js or Bun.
allowed-tools: Bash(gh *) Bash(node *) Bash(bun *)
metadata:
  version: "2.2.3"
  tags: "github, inbox, triage, issues, pull-requests"
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9
  last_synced: "2026-10-05"
  license: MIT
when_to_use: "what needs my attention on GitHub, triage this issue or PR"
---

# GitHub Inbox

Turn scattered GitHub work into a small priority queue.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- Optional repository, owner, or project filter
- Optional limit and priority rules
- `triage <issue-or-PR ref>` to evaluate one inbound item instead of listing the inbox

Outputs:

- Prioritized GitHub inbox summary
- Recommended next actions
- Commands for follow-up inspection
- `triage` mode: a verified recommendation (confirmed, failed or insufficient detail; redundancy and prior-rejection checks) for the maintainer to approve

Creates/Modifies:

- None in report mode
- May label, comment, assign, close, or move items only after approval
- `triage` mode may also write `.out-of-scope/<concept>.md` after approval

External Side Effects:

- Reads GitHub issues, PRs, reviews, checks, and project membership
- Writes GitHub issue/PR/project state only after approval

Confirmation Required:

- Before editing labels, assignees, comments, project fields, or issue state
- Before rerunning workflows
- Before merging or closing anything
- In `triage` mode, before every comment, label, close and `.out-of-scope/` write

Delegates To:

- `github-fix-ci` for failing PR checks
- `pr-comments` (`address` mode) for existing review comments
- `github-review-suggestions` when a PR needs inline review feedback
- `project-board` when the board configuration needs inspection
- `board-sync` when existing item values or delivery evidence need reconciliation
- Recommend `feature-intake` or `bug` to turn an accepted triage item into an execution-ready issue

## Workflow

Resolve `<skill-dir>` to this skill's installed directory through the active
catalog before running a helper. Do not assume a repository checkout or a
provider-specific environment variable.

1. Verify auth:

   ```bash
   gh auth status -h github.com
   gh api user --jq .login
   ```

2. Generate the inbox:

   ```bash
   node <skill-dir>/scripts/github-inbox-report.mjs
   ```

   Common filters:

   ```bash
   node <skill-dir>/scripts/github-inbox-report.mjs --owner shipshitdev
   node <skill-dir>/scripts/github-inbox-report.mjs --repo shipshitdev/shipcode
   node <skill-dir>/scripts/github-inbox-report.mjs --project shipshitdev/1
   node <skill-dir>/scripts/github-inbox-report.mjs --limit 50
   ```

3. Triage order:
   - Review requests
   - Authored PRs with failing checks
   - Assigned P0/P1 or blocking issues
   - Mentions needing a response
   - Stale assigned issues
   - Project-board items missing status or priority

4. For each item, choose one next action:
   - Inspect
   - Fix
   - Reply
   - Defer
   - Reassign
   - Close

5. Ask before applying any writes. When writing, use the smallest command:

   ```bash
   gh issue edit <number> --add-label "priority:P1"
   gh issue comment <number> --body-file <file>
   gh pr review <number> --comment --body-file <file>
   ```

## Rules

- Prefer a short queue over a complete dump.
- Keep review requests above authored work unless production is blocked.
- Treat failing checks as actionable only after reading the failure.
- Do not close or defer user-facing issues without leaving a reason.
- If GitHub search results are noisy, narrow by `--repo`, `--owner`, or `--project` before making recommendations.

## Triage mode

`triage <issue-or-PR ref>` evaluates one inbound report or external PR on a repo
the user maintains. Read [references/triage.md](references/triage.md) for the
steps: gather, redundancy check, prior-rejection check, verify the claim, then
recommend one disposition and wait. Rejected enhancements land in the
`.out-of-scope/` knowledge base ([references/out-of-scope.md](references/out-of-scope.md)).
Every comment it posts starts with the AI disclaimer defined in the triage reference.
