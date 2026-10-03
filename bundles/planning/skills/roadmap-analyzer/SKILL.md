---
name: roadmap-analyzer
description: Turns the ICP in .agents/memory/icp.md into a revenue-ranked roadmap, finding gaps that block landing, retaining, or expanding customers. Use to decide what to build next.
user-invocable: true
argument-hint: "[product or focus area]"
metadata:
  version: "2.2.2"
  tags: "roadmap, product, revenue, mrr, prioritization, icp"
  author: Ship Shit Dev
when_to_use: "what to build next, blocking revenue, plan toward MRR"
---

# Roadmap Analyzer

Rank what to build next by how much revenue it moves, grounded in the ICP. The output
is a backlog a founder can defend to themselves: every item traces to landing,
retaining, or expanding a paying segment.

Read-only on code. It produces analysis, not commits or issues — handoff to
`roadmap-to-milestones` turns the backlog into tracked work.

## Contract

Inputs:

- `.agents/memory/icp.md` (from the `icp` skill) — the segments and their
  land/retain/expand levers. If absent, stop and recommend running `icp` first; a
  roadmap without an ICP ranks by taste, not revenue.
- The codebase and product docs, to inventory what already ships.

Outputs:

- Gap analysis: ICP need vs current state, severity-tagged.
- Revenue-ranked backlog: P0/P1/P2 with a one-line revenue rationale each.
- Strategic themes: 3–5 focus areas, sequenced.

Creates/Modifies:

- None. Read-only.

Delegates To:

- `icp` when no ICP doc exists yet.
- Recommend `roadmap-to-milestones` to turn the ranked backlog into GitHub milestones + issues.
- `feature-intake` / `prd-writer` to expand a single backlog item into a PRD.

## Step 1 — Load the ICP

Read `.agents/memory/icp.md`. Pull out, for the **primary** segment: the acute pain,
the buying trigger, the churn reasons, and the expansion path. These are the three
revenue levers the roadmap serves:

- **Land** — remove what blocks the primary segment from buying.
- **Retain** — remove the named churn reason.
- **Expand** — unlock the stated expansion path (seats, volume, tier).

If `icp.md` is missing, do not guess a customer. Say so and recommend `icp`.

## Step 2 — Inventory what already ships

Discover current capabilities from the code and docs, not from memory. Search for the
product's core actions, automation, collaboration, integration, and billing surfaces.
For each capability record status (production / partial / missing) and quality
(solid / rough / prototype), with a `file:line` anchor as evidence. Give credit for
what exists — the gap is measured against reality, not a blank slate.

## Step 3 — Gap analysis

Compare ICP needs against the inventory. One row per need:

| ICP need (segment) | Lever | Current state | Gap severity |
|---|---|---|---|
| <need> | Land/Retain/Expand | Missing/Partial/Solid | CRITICAL/HIGH/MEDIUM/LOW |

Severity is revenue-weighted: a Land or Retain gap for the **primary** segment is at
least HIGH; a gap for a "not our ICP" segment is LOW no matter how large.

## Step 4 — Rank by revenue, not by effort alone

Score each candidate:

- **Revenue impact (1–5)** — does it Land a new sale, Retain against a churn reason,
  or Expand an account? Land/Retain for the primary segment score 4–5; polish for a
  secondary segment scores 1–2.
- **Urgency (1–5)** — is a sale, renewal, or churn event blocked on it now?
- **Effort (1–5)** — honest build size.

**Score = (Revenue × 2 + Urgency) ÷ Effort.** Higher = sooner.

Then apply the two rules that a naive score misses:

- **Finish over start.** A feature that is *partial* and sits on a revenue lever is
  not a backlog item — it is a churn/lost-sale risk actively leaking money. Rank
  finishing it above starting anything new. A half-shipped core feature is a
  liability, not progress.
- **Sellable over impressive.** Prefer the item that completes a story a customer
  will pay for over the one that adds a new half-story. Ten features at 80% sell
  worse than seven at 100%.

Bucket the ranked list P0 (build now), P1 (next), P2 (later), and pull out
**quick wins** — high revenue impact, low effort — as the fastest MRR movers.

## Step 5 — Strategic themes

Group the backlog into 3–5 themes, each named in the product's own language, each
tied to a revenue lever. Sequence them: foundations that unblock the primary
segment's Land first, then Retain, then Expand. For each theme give a one-line vision,
the ICP segment it serves, and its success metric (ideally a revenue or retention
number, not a vanity metric).

## Output

```markdown
# Roadmap Analysis — <product> (<date>)

## Executive summary
- <3–5 bullets: the revenue story and the single most important next move>

## Gap analysis
<table from Step 3>

## Revenue-ranked backlog
### P0 — build now
1. **<feature>** (score X.X) — Lever: <Land/Retain/Expand>. Why: <revenue rationale>.
### P1 — next
### P2 — later

## Quick wins
- <high-impact, low-effort items>

## Strategic themes
1. **<theme>** — serves <segment>, <lever>. Success: <metric>.

## Recommended next step
Run `roadmap-to-milestones` to sequence P0/P1 into milestones with due dates.
```

## Anti-Patterns

- **Ranking without an ICP.** Without `icp.md`, prioritization is preference. Run
  `icp` first.
- **Effort-first prioritization.** Cheap-and-easy is not the same as revenue-moving;
  the score weights revenue ×2 for a reason.
- **Treating all segments equally.** Optimize for the primary segment; a large gap
  for a non-ICP segment is still LOW.
- **Listing features without a revenue rationale.** Every item names which lever it
  moves, or it does not belong on the backlog.
- **Rewarding new starts over finishing.** Partial features on a revenue lever
  outrank anything new — they are leaking money now.
