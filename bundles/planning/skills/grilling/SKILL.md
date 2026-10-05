---
name: grilling
description: Grills the user relentlessly about a plan, decision, or idea until every branch of the design tree is resolved. Use when stress-testing thinking or when told grill me.
license: MIT
metadata:
  version: "2.2.2"
  tags: "interview, grilling, discovery, planning, frontier"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9
  last_synced: "2026-10-05"
  license: MIT
when_to_use: "grill me, interview me"
---

# Grilling

Interview the user relentlessly until every branch of the **design tree** is resolved. This is the reusable interview primitive. Orchestrators (`interview`, `shape`) invoke it; they own grounding, artifacts, and routing.

## Contract

Inputs:

- A plan, decision, idea, or design question
- Optional repo or docs context already loaded by the calling skill

Outputs:

- Settled decisions across the design tree
- Remaining open questions only when a fact-finding sub-agent is still running

Creates/Modifies:

- None. Calling skills persist briefs, glossaries, or issues.

External Side Effects:

- Read-only lookups to settle facts. No tracker writes, no code edits.

Confirmation Required:

- Before acting on the settled tree. Stop at a shared understanding; do not implement.

Delegates To:

- None. Fact-finding may dispatch a read-only exploration sub-agent.

## Design tree

Map the topic as a **design tree**: every decision branches into the decisions that hang off it.

The **frontier** is every decision whose prerequisites are already settled — the questions that can be asked *now* without guessing at answers not yet heard.

Work the tree in **rounds**. Ask the whole frontier in one round. Wait for answers before the next round.

## Round format

Number each frontier question. Recommend an answer so the user can accept it in a word.

```markdown
**Q1 — <question title>**: <question body, including choices when they exist>

Recommended: <recommended answer>

---

**Q2 — <question title>**: <question body>

Recommended: <recommended answer>
```

Separate the questions of one round with a `---` rule so each reads on its own.

A question whose answer depends on another question still open in this round belongs to a later round, not this one.

## Facts vs decisions

Finding **facts** is the agent's job. When a frontier question needs a fact from the environment (filesystem, tracker, docs), dispatch a sub-agent to find it. Do not ask the user for anything that can be looked up.

Do not block the rest of the frontier on that lookup. A running exploration is an unsettled prerequisite, so only questions downstream of it wait — ask the rest of the frontier now.

**Decisions** are the user's. Put each to them and wait.

## Done when

The **frontier is empty**: every branch of the design tree visited, nothing left silently assumed.

Do not act on the tree until the user confirms a shared understanding.
