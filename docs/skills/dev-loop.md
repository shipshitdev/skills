## What it does

The Dev Loop turns a GitHub issue into a reviewed PR. You are architect and
reviewer. An agent claims a Backlog issue that carries a dispatch gate, implements
it, runs QA, and opens a PR in Human Review.

It is a board-driven pull loop, not a daemon. One invocation works one issue.
Nothing runs until a human opts an issue in with `dispatch:claude`,
`dispatch:codex`, or `dispatch:openrouter`.

## When to reach for it

You invoke the pieces by typing them — `/prd` shapes an idea, `/loop` claims and ships one gated issue. The agent will not
run the loop on its own.

Reach for this when the repo already tracks work on GitHub Issues + a Projects
board and you want agents to execute tickets you have already shaped.

For a vague idea that is not a ticket yet, start at `/prd`.

## Prerequisites

`/setup-agent-routing` once per repo. It writes the `## Agent skills` block and
`docs/agents/{issue-tracker,triage-labels,domain}.md` so the loop skills know the
tracker, labels, and glossary layout.

`bash scripts/setup-dev-loop.sh` (in a consumer repo that vendors the loop
scripts) provisions labels, board, and workflows.

## The chain

`prd-writer` / `feature-intake` → `writing-plans` →
`executing-plans` (drives `qa-reviewer`) → human PR review.

For discovery before a PRD, the upstream mattpocock/skills `grill-me` fits when
installed. `shape` remains an explicit advisory entry point.

Board columns are for humans (Backlog · In Progress · Human Review · Done ·
Deferred). The AI loop's sub-phases ride as `loop:*` labels inside In Progress.

## Common questions

**Does this replace my process?**
No. It is the open, `gh`-driven version of ShipCode's pipeline — same stages, no
app required. You still write the idea and merge the PR.

**Can I run it without GitHub Actions?**
Yes. `/loop` is Phase 1: local pull, Claude lane, one issue at a time. Applying a
dispatch label is Phase 2: headless GitHub Actions.

**Where do PRDs and plans live?**
On the issue. `prd-writer` writes the body. `writing-plans` posts a
`## Implementation Plan` comment. Executors read body plus comments.

## It's working if

- An issue sits in Backlog until you apply a dispatch gate.
- One `/loop` run claims exactly one issue, opens exactly one PR, and exits.
- Human Review is a PR you can merge or kick back — not an agent chatting.
- PRDs and plans are on the issue, not in a local plans folder.

## Where it fits

**Role.** The flagship chain of this catalog.

**Neighbours.** `review-dispatch` is the review front door after a PR exists.
`setup-agent-routing` is the run-once setup.

Full operator map: [`.agents/memory/system/ai-dev-loop.md`](../../.agents/memory/system/ai-dev-loop.md).
