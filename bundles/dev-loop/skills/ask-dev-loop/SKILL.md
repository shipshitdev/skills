---
name: ask-dev-loop
description: Ask which Dev Loop skill or flow fits the current situation. A router over the flagship idea-to-ship path.
user-invocable: false
license: MIT
metadata:
  version: "2.2.2"
  tags: "dev-loop, router, planning, dispatch"
  author: Ship Shit Dev
when_to_use: "which skill, what should I run, ask-dev-loop, how do I start, idea to ship, which flow"
---

# Ask Dev Loop

The human does not remember every skill. Ask.

This is an **advisory router**: name the skill to type next and why, then stop.
Execution routers can invoke reusable engines within an authorized task, but
this skill only recommends. `grilling`, `domain-modeling`, `tdd`, and `debug`
may be named as what the chosen workflow will run.

## Contract

Inputs:

- A situation in plain language (an idea, a bug, a PR, a foggy large effort, a
  setup question, or "I don't know where to start")

Outputs:

- The recommended skill to type, one sentence of why, and the next step after that
- Neighbours when two skills are easy to confuse

Creates/Modifies:

- None

External Side Effects:

- None

Confirmation Required:

- None. Advisory only.

Delegates To:

- None. Name the skill; the human types it.

## Precondition

If `docs/agents/issue-tracker.md` is missing, recommend `/setup-agent-routing`
first. The other engineering skills read that routing block.

## The main flow: idea → ship

The route most work travels.

1. **`/interview`** — sharpen the idea. Repo-grounded; runs `grilling` and
   `domain-modeling`; leaves an interview brief. Start here whenever the working
   directory is a real repo.
2. **Branch — does a design question need a runnable answer?** Detour through
   `/prototype` (throwaway code that answers one question), then return to the
   brief.
3. **Branch — is this a multi-session build?**
   - **Yes** → `/prd write` (`prd-writer`) then `/prd intake` (`feature-intake`)
     or `writing-plans` on the issue, then `/loop` / `executing-plans` per ticket.
   - **No** → `writing-plans` in this session, then `executing-plans` (or just
     implement with `/tdd`).

Keep grilling, spec, and tickets in **one context window**. Each `/loop` /
`executing-plans` run starts fresh from the ticket.

## On-ramps

- **Bugs and incoming requests piling up** → `/prd intake` (`feature-intake`) or
  `github-inbox`. Tickets that `prd-task-creator` already wrote are agent-ready; do not
  re-intake them.
- **Something's broken** → `/debug` (it escalates on its own when previous fixes
  failed). Tight red loop first; no theory without a loop.
- **A huge, foggy effort** → `roadmap-analyzer` / `roadmap-to-milestones` to chart
  the destination, then merge onto the main flow at `/interview` or `/prd write`.
  Do not skip the collapse into a buildable PRD.

## Codebase health

Not feature work — upkeep.

- **`/codebase-advisor`** — survey, produce plans for another agent. Read-only on
  source.
- **`/tech-debt`** — ranked debt register (interest over principal).
- **`codebase-design`** — deep-module vocabulary when the question is the *shape*
  of a module, not an inventory.

## Review

- **`/review`** (`review-dispatch`) — pick the review depth and target.
- **`code-review`** — correctness and security gate, plus spec fidelity against
  the originating issue.

## Standalone

- **`/wait-what`** — the last message did not land; re-pitch it.
- **`grilling`** — the interview primitive with no wrapper. Reach for it only when
  the interview itself is the whole ask.
- **`domain-modeling`** — the words are the problem (fuzzy term, overloaded
  "account", missing ADR).
- **`/wizard`** — steps only a human can perform (dashboards, secrets, cutovers).
- **`fix-merge-conflicts`** — already mid-merge or rebase.

## How to answer

Match the user's situation to one row above. Reply with:

1. The skill to type (slash name when it has a command).
2. Why this one, in one sentence.
3. The neighbour they might have meant, if any.
4. What happens after that skill finishes.

If two flows both fit, ask one question that splits them, then recommend.
