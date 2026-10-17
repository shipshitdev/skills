---
name: show-me-your-work
description: Keeps a TSV decision log (what, why, evidence, result) for long or unattended work. Use for autonomous or multi-phase runs a human reviews afterward.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.5"
  tags: "audit, decisions, trail, verification"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "show me your work, audit log"
---

# Show me your work

For work a human reviews after the fact, a decision trail reconstructs
what was decided, why, and on what evidence.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A long, autonomous, or multi-phase run that needs an audit trail

Outputs:

- One canonical TSV log, plus an Attention section from a
  different-tier review of the trail

Creates/Modifies:

- `decisions.tsv` in the work dir, or `.tmp/audit/<task-slug>.tsv`
  when several efforts run at once
- Commit the log only when a reviewer needs it

External Side Effects:

- None unless the caller commits the trail

Confirmation Required:

- Before committing the log to the repo

Delegates To:

- None. Other skills route their trail here.

## Format

Copy [references/decision-log-template.tsv](references/decision-log-template.tsv)
to start. Columns: `ts`, `phase`, `decision`, `why`, `evidence`,
`result`. Cells stay single-line. Evidence is a pointer, not prose.

Use `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`
so rows stay well-formed.

Log decision points and checkpoints, not every action. Append-only. A
wrong call gets a new row.

Write each entry the way you'd tell a teammate. Apply
`references/prose-slop.md` from the selected `deslop` skill directory to log text.

## Audit the log

Before handing back, walk the log against what actually happened in
this run's transcript (the path the harness names). Cut invented rows.
Add missing forks. Drop padding.

## Cross-tier review

Spawn a subagent on a different capability tier or family from the
one that did the work. It reads the trail and the transcript, then
flags weak evidence, skipped verification, and risky choices.

Every reply for a run that produced a trail ends with an Attention
section. Lead with the reviewer's capability tier, then list flags.
"No flags" is valid. Never name a concrete model.

## Show Me Your Work procedure

Read [show-me-your-work procedure](references/show-me-your-work-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
