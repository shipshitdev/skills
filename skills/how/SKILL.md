---
name: how
description: "Explains how a subsystem works: architecture, runtime flow, onboarding mental models; can critique architecture. Use for how does X work or code walkthroughs. Not for motivation."
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "56bfd14418fa733e34d98f714f357d28788470e3"
  version: "2.2.2"
  tags: "architecture, walkthrough, onboarding, critique"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/how/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "where does this belong, ownership"
---

# How

Explore the codebase to answer "how does X work?" Produce an architectural
explanation at the level of a senior engineer onboarding onto a subsystem.

Two modes:

1. **Explain** (default). Explore and produce a clear explanation.
2. **Critique.** Explain first, then spawn independent critics.

Companion to `why`. This skill answers what the code does. `why` answers
what forces led to its shape.

## Contract

Inputs:

- A how-question: subsystem, feature flow, architectural overview, or
  runtime trace

Outputs:

- The structured explanation below
- In Critique mode, a lead verdict over critic findings

Creates/Modifies:

- None

External Side Effects:

- None. Read-only exploration.

Confirmation Required:

- None

Delegates To:

- None. May spawn read-only explorer, explainer, and critic subagents.

## Explain mode

### Step 1. Understand the question

Parse the ask. If ambiguous, state the best-guess interpretation and
proceed. Do not ask. Let the user redirect.

**Simple** (one module, a narrow function): skip explorer agents. The
explainer explores and explains in one pass.

**Complex** (multiple files or services, a cross-cutting feature): spawn
2-4 parallel explorers, then one explainer. When in doubt, lean simple.

### Step 2a. Explore (complex only)

Decompose into 2-4 distinct slices so explorers do not duplicate work.
Spawn all explorers in one message on the fast cheap tier, read-only.
Each explorer gets [references/explorer-prompt.md](references/explorer-prompt.md)
plus its slice. Each traces input to output without hand-waving.

### Step 2b. Direct explain (simple)

Spawn one read-only explainer on the strongest judgment tier. It explores
and writes the explanation. Use
[references/explainer-prompt.md](references/explainer-prompt.md).

### Step 3. Synthesize (complex only)

Once explorers return, spawn one explainer on the strongest judgment
tier with all findings. It reconciles overlap and contradictions.

### Step 4. Present

Present the explainer's output. Light edits for clarity are fine. Do not
substantially rewrite.

## Output format

**Overview.** 1-2 paragraphs. What it is, what it does, why it exists.

**Key Concepts.** The types, services, or abstractions needed to follow
the rest.

**How It Works.** The flow: trigger, steps, data, decision points. Prose,
not pseudocode. Cite files and functions.

**Where Things Live.** A brief map of the relevant files.

**Gotchas.** Non-obvious edges and historical scars.

## Critique mode

Triggered when the user asks for architectural issues, not just
understanding.

1. Run the full explain flow.
2. Spawn one architectural critic per available judgment family, all in
   one message, read-only, on mixed capability tiers. Each gets the
   explanation, file paths, [references/critic-prompt.md](references/critic-prompt.md),
   and [references/critique-rubric.md](references/critique-rubric.md).
3. Lead judgment. Categorize findings: Act on, Consider, Noted, Dismissed.
   Present the explanation first, then the critique.

## How procedure

Read [how procedure](references/how-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
