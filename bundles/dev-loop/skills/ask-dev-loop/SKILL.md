---
name: ask-dev-loop
description: Ask which Dev Loop skill or flow fits the current situation. A router over the flagship idea-to-ship path.
user-invocable: false
license: MIT
metadata:
  version: "2.2.4"
  tags: "dev-loop, router, planning, dispatch"
  author: Ship Shit Dev
when_to_use: "which skill, what should I run, ask-dev-loop, how do I start, idea to ship, which flow"
---

# Ask Dev Loop

The human does not remember every skill. Ask.

This is an **advisory router**: name the skill to type next and why, then stop.
Execution routers can invoke reusable engines within an authorized task, but
this skill only recommends. `grill-me`, `domain-modeling`, `tdd`, and `debug`
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

1. **`/interview`** — sharpen the idea. Repo-grounded; runs `grill-me` and
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
4. **When a PR is written** → `github-pr-publish` (its body template: Summary
   with a visual, Evidence, Merge danger), so the reviewer sees the point fast.
5. **When the run ends** → `/retro` if it was harder than it should have been, so
   the friction becomes a check, a pointer or a skill edit.

Keep grilling, spec, and tickets in **one unbroken context window**: the answers
to the grilling are the spec's raw material. Each `/loop` / `executing-plans` run
starts fresh from the ticket. Phase boundaries below decide the rest.

## Phase boundaries

A phase ends when its artifact is written (brief, spec, plan, ticket, PR). Decide
what happens to the context at that boundary, not mid-phase. Ordered; the first
yes wins:

1. **Continue** when the next phase's primary source is already in this window
   and the window is still in the smart zone (about 150k tokens).
2. **`/clear`** when everything the next phase needs lives in files or issues and
   this context is disposable.
3. **`/handoff`** only when the work moves to a new harness, a new directory or
   repository, a colleague, or forks a side task mid-phase. It is the narrow
   branch, not the default.
4. **Subagent** when the work is scoped tightly enough to run AFK and return one
   summary.
5. **`/compact`** when nothing above fits. Pass an instruction naming what to keep.

## On-ramps

- **Bugs and incoming requests piling up** → `/prd intake` (`feature-intake`) or
  `github-inbox`. Tickets that `prd-task-creator` already wrote are agent-ready; do not
  re-intake them.
- **Something's broken** → `/debug` (it escalates on its own when previous fixes
  failed). Tight red loop first; no theory without a loop. Afterwards `/retro`
  asks what would have prevented it.
- **A huge, foggy effort** (too big for one session, decisions still unmade) →
  `/wayfinder`: a map of decision tickets resolved one per session, then merge
  onto the main flow at `/prd prepare`. Do not skip the collapse into a buildable
  PRD. (`roadmap-analyzer` and `roadmap-to-milestones` rank ICP and revenue; they do
  not map decisions. For one large run whose decisions are already made, use
  `figure-it-out`.)
- **A decision only someone else can answer** → `/interview send`: a questionnaire
  for that person.
- **An outside issue or PR to evaluate** → `github-inbox` with `triage <ref>`.
- **A fact to look up from primary sources** → `research` (a cited note).

## Codebase health

Not feature work — upkeep.

- **`codebase-design survey`** — survey, produce plans for another agent. Read-only
  on source. `report` writes an analysis for humans; `deepen` ranks deepening
  candidates.
- **`/tech-debt`** — ranked debt register (interest over principal).
- **`codebase-design`** — deep-module vocabulary when the question is the *shape*
  of a module, not an inventory.

## Review

- **`/review`** (`review-dispatch`) — pick the review depth and target.
- **`code-review`** — correctness and security gate, plus spec fidelity against
  the originating issue.
- **`/retro`** — a session was harder than it should have been; turn its
  friction into checks, pointers and skill edits. Also the follow-up to `/debug`
  and the end of the main flow.

## Standalone

- **`/handoff`** — a phase must continue in a new harness, directory, repo or
  colleague's hands; writes one file a fresh agent can pick up. Narrow branch of
  Phase boundaries, not a default.
- **`/wait-what`** — the last message did not land; re-pitch it.
- **`grill-me`** — the interview primitive with no wrapper. Reach for it only when
  the interview itself is the whole ask.
- **`domain-modeling`** — the words are the problem (fuzzy term, overloaded
  "account", missing ADR).
- **`/wizard`** — steps only a human can perform (dashboards, secrets, cutovers).
- **`fix-merge-conflicts`** — already mid-merge or rebase.

## Prompt wording

- **`pstack`** — when the question is how to word the request itself, name the
  `pstack` skill's prompting reference: goal, a done check that can fail, the
  proof to show, and what to leave out.

## How to answer

Match the user's situation to one row above. Reply with:

1. The skill to type (slash name when it has a command).
2. Why this one, in one sentence.
3. The neighbour they might have meant, if any.
4. What happens after that skill finishes.

If two flows both fit, ask one question that splits them, then recommend.
