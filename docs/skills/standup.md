# Standup: personal, all, audit

Use one entry point with simple positional arguments. Bare numbers mean hours.

| Invocation | Result |
|------------|--------|
| `/standup` or `/standup 24` | Personal author-filtered local activity over 24 hours |
| `/standup all 24` | Everyone's changes integrated into the live default branch over 24 hours |
| `/standup all 24 audit` | The same frozen integrated scope plus individual and combined review |
| `/standup all 7d audit` | Seven elapsed days of integrated changes and review |
| `/standup all since <full-SHA> audit` | All reachable changes after an ancestor checkpoint through the frozen branch tip |
| `/standup all from 2026-10-01T09:00 to 2026-10-02T09:00 --timezone Europe/Malta audit` | Explicit dated scope with timezone and review |
| `/standup all 7d --scope apps/api audit` | Path-scoped audit including required cross-package consumers |

`24h` also works. Hours/days/weeks are elapsed durations; dated windows resolve to
absolute instants. The time interval is `(start, end]`. All-author modes include
automation, direct pushes, squash/rebase histories, merge resolutions, and
reversions. They follow integration evidence rather than author dates. Personal
mode retains `--author`, `today`, `yesterday`, and `--all-repos`.

All-author recap reads diffs and returns frozen BASE/END, PR links, inventory
coverage, and available deployment evidence. It performs no correctness review
and proposes no audit checkpoint. The trailing `audit` adds correctness/spec and
cross-commit review, review-history links, exact-SHA CI/environment evidence,
prioritized findings, unresolved gaps, and a proposed safe next checkpoint.

A green merged PR does not prove deployment. Missing timing/history/lenses or
uninspected required consumers prevent a complete audit claim and checkpoint
advancement. Unresolved findings and operational evidence gaps carry forward even
after code review coverage is complete. A scoped checkpoint cannot stand in for
whole-repository coverage. Reports/checkpoints stay in the response.

## Choose the workflow

| Need | Owner |
|------|-------|
| What did I work on? | `standup` personal mode |
| What merged from everyone? | `standup all <window>` |
| Double-check everything merged | `standup all <window> audit` |
| Customer-facing release notes | `changelog-generator` |
| Write a commit message / prepare local commits | `commit-summary` |
| Review one diff/PR or a local-HEAD retrospective | `review-dispatch` |
| Board, issues, code, operations, and cleanup maintenance | `weekly-review` |

The [standup skill](../../skills/standup/SKILL.md) resolves the installed
`weekly-review` resource `references/merged-history.md`. That
[shared history procedure](../../skills/weekly-review/references/merged-history.md)
owns freeze/inventory/recap/audit behavior; standup does not invoke weekly board
maintenance. Audit uses the installed `code-review` and `full-code-review` engines
with explicit historical diffs. Missing dependencies are reported as unavailable;
they are never installed implicitly. The dev-workflow bundle already includes
these companions. Individual-skill consumers need the companions installed.

Every standup mode is report-only: no repair, merge, deployment, CI rerun,
issue/comment write, scheduling, or policy change. `--fix` is rejected. Acting on
findings or saving a report is a separate authorized task.

## Verification boundary

Repository lint, skill validation, version checks, and regenerated bundle checks
verify source and distribution consistency. Independent review checks the written
workflow against integration/reversion/checkpoint scenarios. These checks do not
prove a live consumer agent follows the instructions or that a source host exposes
complete push/deployment history. Record those limitations in each real report.
