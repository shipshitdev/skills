---
name: figure-it-out
description: Designs an auditable playbook when no narrower one fits. Use for a large migration, an ambitious multi-part change, or work a human reviews later. Logs via show-me-your-work.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.3"
  tags: "playbook, migration, audit, hypothesis"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/figure-it-out/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "figure it out, no playbook fits"
---

# Figure it out

When the task matches no `pstack` playbook, design one. The deliverable
before any code is the workflow itself. Bias toward more rigor.

Do not reinvent a playbook you already have. A focused single-unit task
routes to Bug fix, Perf, Feature, Visual parity, Eval, or Multi-phase
plan. A large or cross-cutting version of one belongs here.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A large, cross-cutting, or unattended task with no narrower playbook

Outputs:

- A designed phase list, a rigor level, a decision trail, and
  verification against a falsifiable predicate

Creates/Modifies:

- The work the designed playbook authorizes
- A decision log via `show-me-your-work`

External Side Effects:

- Whatever the designed playbook later requires

Confirmation Required:

- One checkpoint before a multi-hour run

Delegates To:

- File pointer: `references/principles.md` from the selected `pstack` skill directory
- `architect`, `arena`, `show-me-your-work` for authorized investigation

## Start

Open a todo list whose first item is reading
`references/principles.md` from the selected `pstack` skill directory. Then add the phases below.

## Phase A: Frame

State a falsifiable done predicate, quantified scope, and a rigor
level biased high. Present framing before a long run. Reversible work
proceeds. A multi-hour run earns one checkpoint.

## Phase B: Design the workflow

Decompose into independently-landable units. Sequence
riskiest-unknown-first. Build the verification harness before the
work, with a baseline from the pre-change state.

For one-way-door design decisions, run `architect` (it runs `arena`).
Skip it for mechanical work whose shape is already concrete.

Parallelize only across genuine seams. Give each worker its own
worktree or branch. Write the designed phase list down.

## Phase C: Run the loop

Each unit is an experiment: hypothesis, smallest change, measure on
the real artifact, keep or revert. Verify each unit before the next.
A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is
not a pass.

## Phase D: Keep the audit trail

Log via `show-me-your-work`. Commit the trail when a reviewer needs it
to trust the result.

## Phase E: Verify and hand back

Check the whole against the Phase A predicate on the real product.
Encode a recurring correction as a gate, lint, check, or script.

**Reply:** the playbook you designed, the rigor level and why, the
trail path, what's verified, what's still open.

## Figure It Out procedure

Read [figure-it-out procedure](references/figure-it-out-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
