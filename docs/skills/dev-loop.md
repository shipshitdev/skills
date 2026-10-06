## What it does

The Dev Loop turns a GitHub issue into a reviewed PR. You are architect and
reviewer. An agent claims a Backlog issue that carries a dispatch gate, implements
it, runs QA, and opens a PR in Human Review.

It is a board-driven pull loop, not a daemon. One invocation works one issue.
Nothing runs until a human opts an issue in with `dispatch:claude`,
`dispatch:codex`, or `dispatch:openrouter`.

## When to reach for it

You invoke the pieces by typing them — `/ask` names which one, `/interview`
sharpens an idea, `/loop` claims and ships one gated issue. The agent will not
run the loop on its own.

Reach for this when the repo already tracks work on GitHub Issues + a Projects
board and you want agents to execute tickets you have already shaped.

For a one-off "which skill?" question, use [ask-dev-loop](ask-dev-loop.md). For a
vague idea that is not a ticket yet, start at `/interview`.

## Prerequisites

`/setup-agent-routing` once per repo. It writes the `## Agent skills` block and
`docs/agents/{issue-tracker,triage-labels,domain}.md` so the loop skills know the
tracker, labels, and glossary layout.

`bash scripts/setup-dev-loop.sh` (in a consumer repo that vendors the loop
scripts) provisions labels, board, and workflows.

## The chain

`interview` → `prd-writer` / `feature-intake` → `writing-plans` →
`executing-plans` (drives `tdd` + `qa-reviewer`) → human PR review.

`grill-me` and `domain-modeling` run underneath `interview`. They are
reusable engines. A selected workflow can invoke them within its existing scope.
Delegation preserves report-only restrictions and action gates. `/ask`,
`interview`, and `shape` remain explicit advisory entry points.

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

**What if I don't know which skill to type?**
`/ask` (`ask-dev-loop`). It hints. It does not fire the other user-invoked
skills.

## It's working if

- An issue sits in Backlog until you apply a dispatch gate.
- One `/loop` run claims exactly one issue, opens exactly one PR, and exits.
- Human Review is a PR you can merge or kick back — not an agent chatting.
- PRDs and plans are on the issue, not in a local plans folder.

## Where it fits

**Role.** The flagship chain of this catalog.

**Neighbours.** [ask-dev-loop](ask-dev-loop.md) is the index over the chain.
`review-dispatch` is the review front door after a PR exists.
`setup-agent-routing` is the run-once setup.

Full operator map: [`.agents/memory/system/ai-dev-loop.md`](../../.agents/memory/system/ai-dev-loop.md).
