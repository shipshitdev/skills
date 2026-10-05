## What it does

A router over the flagship Dev Loop. You describe a situation; it names the skill
to type and why. It hints. It does not fire other user-invoked skills.

Its contract is advisory: asking which workflow fits should return a recommendation.
Execution routers such as `/test run` can run their declared engines, but `/ask`
stops at the recommendation so you can choose the next task.

## When to reach for it

You invoke this by typing `/ask` — the agent will not reach for it on its own.

Reach for this when the question is "which skill do I run?" For actually
sharpening an idea, type `/interview` instead. For shipping a gated ticket, type
`/loop`.

## Prerequisites

Useful after `/setup-agent-routing` has configured the repo. The router still
works as a map if setup has not run; it will send you there first.

## The map it holds

- Main flow: idea → `/interview` → PRD / intake → plan → `/loop`
- On-ramps: bugs (`debug`), incoming requests (`feature-intake`), foggy large
  work (`roadmap-analyzer`)
- Phase boundaries: continue, `/clear`, `handoff`, subagent, `/compact`, in that order
- Upkeep: `codebase-advisor`, `tech-debt`, `codebase-design`
- Review: `/review`
- Standalone: `/wait-what`, `wizard`, `prototype`

Keep `ask-dev-loop`'s `SKILL.md` in sync when a user-reachable Dev Loop skill is
added, renamed, or rerouted.

## Common questions

**Why doesn't it just run the skill for me?**
Because `/ask` promises advice, not execution. Its explicit entry point stays off
the model's automatic discovery list. Other routers can run reusable engines
within a selected task; that never expands the user's authorization.

**Is this the same as `/prd` or `/review`?**
Those are front doors for one domain (PRDs, reviews). `/ask` is the map over the
whole Dev Loop, including those front doors.

**What if two flows both fit?**
The skill asks one splitting question, then recommends. It does not pick a
compromise skill.

## It's working if

- You leave with one skill to type, not a menu of five.
- The neighbour you might have meant is named in one clause, not a second essay.
- After you type the recommended skill, you do not need `/ask` again until the
  next phase boundary.

## Where it fits

**Role.** Run-once orientation, then a reach-for-it-anytime index.

**Neighbours.** The [Dev Loop](dev-loop.md) is the chain this router describes.
`review-dispatch` is the review-only front door.

Point back here whenever a flagship skill is added or renamed.
