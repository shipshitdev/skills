# Writing for agents

The levers that extend `.agents/memory/system/skill-standards.md` "Writing craft"
(leading words, completion criteria, pointers, hierarchy, no-ops, positive
prompts). Apply them to anything an agent reads: a skill, an `AGENTS.md` or
`CLAUDE.md`, a doc reached through a pointer. Packaging differs; the writing does
not. Each lever aims at the same result: the agent takes the same process every
run, not the same output.

Adapted from `writing-for-agents` in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT, commit
`4588b32ecab9`). Owned here; not a sync target.

## Two loads

Every document or pointer you add spends one of two budgets:

- **Context load**: always-loaded text (a steering line, a skill description)
  that costs tokens and attention on every turn, fired or not.
- **Cognitive load**: the human's cost of remembering which documents exist and
  when to reach for each. The human is the index. Spend it where human judgement
  matters; remove it where it does not.

A pointer buys escape from context load at the price of its own line. Material
with no pointer rides entirely on cognitive load. Name the load a new document
spends before adding it.

## Co-location

The hierarchy decides how far down a piece sits; co-location decides what sits
beside it. Keep a concept's definition, rules and caveats under one heading so
reading one part brings its neighbours along. Test: the document reads like
documentation written for the agent. Scattered fragments of one meaning fail it.
(Duplication repeats a meaning in two places; scattering splits one meaning
across many.)

## Sprawl

A document too long even when every line is live and unique. Attention thins
across the excess and each extra line is one more to keep current. Cure with the
hierarchy: disclose reference behind pointers, split by branch or sequence, so
each path carries only what it needs.

## Split by sequence

Split a run of steps when the later steps tempt the agent to rush the one in
front of it. Hiding them forces more legwork on the current step. Order of
defence:

1. Sharpen the step's completion criterion (cheap and local).
2. Split only when the bound stays fuzzy and you have watched the rush happen.

Hiding works only across a real context boundary: a handoff or a subagent
dispatch. An inline call leaves the later steps in context and hides nothing.
The reverse also holds: merging two sequences exposes each step to what follows
it.

## The environment is a cache source

`package.json` scripts, config files, directory layout and `--help` output are
sources of truth. A document that restates them is a **cache**: a copy of a
lookup, worth its load only when the lookup is expensive. Cache what looking
cannot reveal: the unwritten convention, the reason behind a choice, the gotcha
no config confesses. Leave one-file, one-command lookups to the environment,
where they cannot go stale.

## Sediment

Without a pruning habit, steering files accrete stale layers because adding feels
safe and removing feels risky, until nothing live can be found under them. Check
each line for relevance on every edit: does it still bear on what the document
does? A line loses relevance by never bearing on the task, or by going stale as
the world it describes changes. Keep one source of truth per meaning, so a
behaviour change is a one-place edit and no copy inflates a rule's prominence.

## Grade the leading word

The no-op test also grades leading words. A word too weak to beat the default
(`be thorough`, when the agent is already thorough-ish) is a no-op. Reach for a
stronger pretrained word (`relentless`, `exhaustive`) instead of a new technique.
Run the document to settle a disagreement about the default; debate settles
nothing.
