---
description: "Recap what you shipped, or what everyone merged, over a time window; add audit to double-check it."
argument-hint: "[all] [24|7d|today|yesterday|since <ref|date>|from <date> to <date>] [audit] [--author <email>] [--all-repos <dir>] [--branch <name>] [--scope <path>] [--timezone <IANA-zone>]"
disable-model-invocation: true
---

# Standup

Return a personal engineer recap by default. Use `all` for everyone's changes
integrated into the selected default branch, and add `audit` for review.

## Usage

```text
/standup                         # personal, last 24 hours
/standup 24                      # personal, last 24 hours
/standup 7d
/standup today
/standup yesterday
/standup since <ref|date>
/standup --author <email>
/standup --all-repos <dir>
/standup all 24                  # all-author integrated recap
/standup all 24 audit            # opt-in integrated-history review
/standup all 24h audit
/standup all 7d audit
/standup all since <full-SHA> audit
/standup all from 2026-10-01T09:00 to 2026-10-02T09:00 --timezone Europe/Malta audit
/standup all 7d --scope apps/api audit
```

`/standup help` prints this Usage block and stops without running anything.

Pass the mode, window/checkpoint, timezone, repository, and limits to the
`standup` skill. Bare positive numbers mean hours. Default to personal and `24h`;
all-author mode needs no configured personal author. Resolve its shared
`weekly-review` history resource through the installed catalog without running
board maintenance. Preserve report-only limits across every review delegate.

Personal mode retains author filtering and optional sibling-repository reporting.
All mode accepts optional explicit `--branch` / `--scope`; reject personal author
and sibling-sweep flags there. Require `all` for the trailing `audit` token. Reject
unknown/conflicting arguments, including `--fix`, and show usage without guessing.

Return integrated recap scope, full BASE/END, PR links, coverage limitations, and
delivery evidence in all mode. Audit adds individual/combined review, findings,
review/CI/deployment receipts, unresolved gaps, and a safe proposed checkpoint.
Keep reports/checkpoints in the response. No invocation grants repair, merge,
deploy, CI rerun, issue/comment write, scheduling, or policy authority. Recommend
`changelog-generator` for customer release notes and `weekly-review` for weekly
maintenance.
