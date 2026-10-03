---
name: swarm
description: Fans out N parallel workers, drains them, and returns one aggregated report. Use for swarm this, parallel coverage, races, gauntlets and exploration partitions.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "56bfd14418fa733e34d98f714f357d28788470e3"
  version: "2.2.2"
  tags: "fan-out, coverage, race, report"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/swarm/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "race N workers"
---

# Swarm

Fan out N parallel workers. They may cover separate slices, race the
same brief, or mix both. The parent waits, aggregates, and returns one
report.

Companion to `arena`, which picks a base and grafts. Companion to
`multi-agent-patterns`, which designs architectures. This skill runs
one operational fan-out.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A done predicate and the report the swarm must return
- Shape: partition, race, or mix
- Optional N

Outputs:

- One consolidated report with a result table, issue one-liners, and
  gaps or dropouts

Creates/Modifies:

- Per-worker output under worktrees or
  `.tmp/swarm-<slug>/worker-<n>/` when workers write

External Side Effects:

- None beyond what each worker's brief authorizes

Confirmation Required:

- None for the swarm itself

Delegates To:

- `worktree` when workers need isolated checkouts

## Phases

Open a todo list: Frame, Fan out, Aggregate, Report.

### A. Frame

State the done predicate. Choose the shape. For a race, declare
`first pass`, `rank all`, or `best-of` before spawning. Set N. Default
workers to the fast cheap tier. For a model-family race, name each
arm's capability tier up front.

### B. Fan out

Spawn all N workers in one message. Every brief stands alone: goal,
scope, slice or race arm, how to verify, what to report. Reports use
`PASS`, `ISSUES`, or `BLOCKED` with evidence.

### C. Aggregate

Read the terminal results. For coverage, every required slice needs a
result. For a race, apply the selection rule declared up front. Do not
paste raw worker dumps.

### D. Report

Return one in-chat report: table, issue one-liners, gaps or dropouts,
and the race rule when used.

## Swarm procedure

Read [swarm procedure](references/swarm-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
