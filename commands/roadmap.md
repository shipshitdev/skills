---
description: "Product planning chain: document the ICP, rank the backlog by revenue, and schedule dated milestones."
argument-hint: "[icp|analyze|milestones|burndown]"
disable-model-invocation: true
---

# Roadmap - ICP → revenue-ranked backlog → dated milestones

One entry point for the product-planning chain that turns "who pays us" into a
scheduled roadmap: document the ICP, rank the backlog by revenue, then sequence it
into GitHub milestones with due dates.

## Usage

```bash
/roadmap icp          # discover + document the Ideal Customer Profile → .agents/memory/icp.md
/roadmap analyze      # ICP → gap analysis + revenue-ranked backlog + strategic themes
/roadmap milestones   # ranked backlog → GitHub milestones with due dates + issue assignment
/roadmap burndown     # progress per open milestone (closed/total, overdue, empty)
/roadmap              # show where you are in the chain and the next step
```

`/roadmap help` prints this Usage block and stops without running anything.

## The chain

Each stage feeds the next; run them in order the first time, then re-run any stage
as things change.

1. **`icp`** → the `icp` skill. Grounds in the product's own copy and code, grills
   for segment / pain / willingness-to-pay / buying trigger / churn, and writes
   `.agents/memory/icp.md` after you approve the draft. Everything downstream ranks
   against this.
2. **`analyze`** → the `roadmap-analyzer` skill. Reads `.agents/memory/icp.md`, inventories what
   already ships, and ranks gaps by revenue impact (Land / Retain / Expand), with a
   finish-over-start rule so half-shipped core features outrank new starts.
3. **`milestones`** → the `roadmap-to-milestones` skill. Turns the ranked backlog
   into dated GitHub milestones (created only after you approve the plan) and assigns
   issues, leaving the dev-loop board's `Status` column untouched.
4. **`burndown`** → `roadmap-to-milestones` in report mode.

## Gates

- `icp` writes one local memory file, only after you approve the draft.
- `analyze` is read-only — it produces analysis, not issues or commits.
- `milestones` creates and edits GitHub milestones and issue assignments only behind
  the skill's confirmation gate; it never changes board `Status` or deletes anything.
- If a stage's input is missing (no ICP for `analyze`, no ranked backlog for
  `milestones`), the skill stops and points you back one stage — it does not guess.
