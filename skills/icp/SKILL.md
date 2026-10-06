---
name: icp
description: Documents a product's Ideal Customer Profile as .agents/memory/icp.md, with segments ranked by revenue potential. Use for define our ICP or before roadmap prioritization.
user-invocable: true
argument-hint: "[product or repo]"
metadata:
  version: "2.2.3"
  tags: "icp, customer, product, revenue, discovery, positioning"
  author: Ship Shit Dev
when_to_use: "who is our customer, who are we selling to"
---

# ICP

Produce one durable artifact: `.agents/memory/icp.md`, the ranked answer to "who do
we sell to, and why do they pay." It is the input that lets `roadmap-analyzer` weigh
features by revenue instead of guesswork, and lets `roadmap-to-milestones` sequence
work toward MRR. Ground it in what the product already says about itself before
asking the founder anything.

This skill does not build features or write roadmaps. It interviews, then writes the
ICP doc — and writes it only after the draft is confirmed.

## Contract

Inputs:

- A product, repo, or business the ICP describes.
- Optional: landing/pricing copy, existing customers, sales notes, analytics,
  churn data, or the founder's own knowledge.

Outputs:

- A ranked ICP draft shown in chat.
- On confirmation, `.agents/memory/icp.md` written (created or updated).

Creates/Modifies:

- `.agents/memory/icp.md` only, and only after the user approves the draft.

External Side Effects:

- None. Reads local product context; writes one local memory file on approval.

Confirmation Required:

- Before writing or overwriting `.agents/memory/icp.md`. Show the full draft first.

Delegates To:

- `roadmap-analyzer` once the ICP exists — it scores features against these segments.
- Recommend `interview` when the question is a single feature's requirements, not the whole
  customer.

## Workflow

### 1. Read what the product already claims

Before any question, mine the product's own signals — the founder should never be
asked what the repo already states:

- Landing page, pricing page, and onboarding copy (who it addresses, what tier
  language implies about budget).
- `.agents/memory/` (especially `memory.md`, `context.md`) and README for stated
  audience or positioning.
- The codebase for feature signals that imply a user: team/roles/permissions →
  multi-seat buyers; batch/bulk/queue → volume users; billing tiers → price points.
- Any existing `.agents/memory/icp.md` — if present, this run refines it, not
  replaces it blind.

Summarize the scan in three bullets: who the product seems built for, what pricing
implies about budget, and where the audience is still ambiguous.

### 2. Grill toward the dimensions that move revenue

Ask at most three questions at a time. Ground each in the scan — never ask what step
1 already answered. The dimensions that decide whether a segment is worth building
for, in priority order:

1. **Segment** — a nameable group, not "everyone". Who has this problem acutely
   enough to pay?
2. **Job-to-be-done** — the outcome they hire the product for, in their words.
3. **Acute pain** — what breaks today without it, and how often. Vitamin or painkiller?
4. **Willingness to pay** — real budget and who signs. A segment that loves the
   product but cannot pay is not the ICP.
5. **Buying trigger** — the event that turns "interesting" into "purchased" (a
   deadline, a scale threshold, a competitor loss, a new hire).
6. **Current alternative** — what they use now (a competitor, a spreadsheet, an
   intern, nothing). The alternative sets the price ceiling and the switching cost.
7. **Churn / abandonment** — why this segment leaves or never activates. This is the
   signal `roadmap-analyzer` needs to score retention work.
8. **Expansion path** — what makes them pay *more* over time (seats, volume, tiers).

Stop when each in-scope segment has these eight filled or explicitly marked unknown.
Do not interrogate past that — a thin but honest ICP beats an invented rich one.

### 3. Rank segments by revenue potential

Order segments by realistic revenue contribution, not by how many exist. For each,
weigh: budget × how acute the pain × how fast they buy × how well the product
already serves them. Name a single **primary** segment — the one the roadmap should
optimize for — and mark the rest secondary or "not yet". A founder serving three
segments equally is usually serving none well; say so.

### 4. Draft the ICP doc

Show this in full and wait for approval before writing:

```markdown
# ICP — <product>

_Last updated: <date>. Maintained by the `icp` skill; consumed by
`roadmap-analyzer` and `roadmap-to-milestones`._

## Primary segment: <name>

- **Who:** <company size / role / context>
- **Job-to-be-done:** <the outcome, in their words>
- **Acute pain:** <what breaks today, how often, painkiller vs vitamin>
- **Willingness to pay:** <budget range, who signs the check>
- **Buying trigger:** <the event that converts them>
- **Current alternative:** <what they use now; the price ceiling it sets>
- **Churn / abandonment reasons:** <why they leave or never activate>
- **Expansion path:** <what makes them pay more over time>
- **Why primary:** <one line on revenue leverage>

## Secondary segments

### <name> — <one line, why secondary / when to revisit>
<same eight fields, briefer>

## Not our ICP (explicitly)

- <segment we will not optimize for, and why — guards against scope creep>

## Revenue implications for the roadmap

- **Land:** <what unblocks a sale to the primary segment>
- **Retain:** <what churn reason the roadmap must remove>
- **Expand:** <what unlocks the expansion path>

## Open questions

- <unknown to validate with real customers, or "None">
```

### 5. Write on confirmation

Only after the user approves, write `.agents/memory/icp.md` (create the directory if
absent). Report the path and recommend the next step: `roadmap-analyzer` to turn this
into a revenue-ranked backlog.

## Anti-Patterns

- **"Everyone" as a segment.** If it does not exclude anyone, it does not guide a
  roadmap. Force a nameable primary segment.
- **Confusing users with buyers.** The person who loves the product and the person
  who pays are often different; capture both under willingness-to-pay.
- **A rich ICP invented from nothing.** Mark unknowns as unknown and put them in Open
  Questions rather than fabricating budget or triggers.
- **Writing the file before approval**, or silently overwriting an existing ICP —
  show the draft and diff the change first.
- **Ranking segments by headcount instead of revenue.** The biggest group is not the
  ICP; the one that pays most, fastest, for the most acute pain is.
