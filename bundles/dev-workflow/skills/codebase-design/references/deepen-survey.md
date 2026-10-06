# Deepen

Adapted from `improve-codebase-architecture` in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, commit `4588b32ecab9`, 2026-10-05). Owned here; not a sync target.

The `deepen` mode of the [survey workflow](./survey.md): find **deepening
opportunities**, refactors that turn shallow modules into deep ones, for
testability and AI-navigability. Recon (Phase 1) runs first as usual; this
reference replaces Phases 2 to 4. The survey stays read-only on source:
candidates and an optional report, never the refactor.

Use the glossary in `SKILL.md` exactly (module, interface, depth, seam, adapter,
leverage, locality) and read it before the first candidate. Name domain concepts with the repo's glossary (`CONTEXT.md`, or
`GLOSSARY.md` when the repo uses it), so a seam is "the Order intake module",
not "the FooBarHandler". Read the glossary and any ADRs in the touched area
before exploring.

## 1. Scope by hot spot

Deepening pays off where change keeps landing, so decide where to look before
looking:

- A direction the user named (module, subsystem, pain point) wins; skip the rest
  of this step.
- Otherwise read `git log --name-only` over a good stretch of history and rank
  paths by how often they change. Let the top paths pull attention first.
- Scattered changes with no hot spot: widen the net and say so.

Done when the scope is named in one sentence with its evidence.

## 2. Explore for friction

Use one read-only exploration subagent, or walk the code directly when none is
available. Follow friction, not a checklist:

- Understanding one concept means bouncing between many small modules.
- A module is **shallow**: its interface is nearly as complex as its
  implementation.
- Pure functions extracted only for testability while the real bugs hide in how
  they are called (no **locality**).
- Tightly coupled modules leak across their seams.
- Code that is untested or hard to test through its current interface.

Apply the **deletion test** to each suspect: delete it in your head. If the
complexity concentrates in the callers, the module earns its keep. If the
complexity vanishes, it was a pass-through. If it only moves, it is a wash.
Keep the candidates where deletion concentrates complexity into one place.

Done when every candidate has survived the deletion test and cites `file:line`
evidence.

## 3. Present candidates

One table, strongest first, no interfaces yet:

| # | Files | Problem | Change in plain words | Benefit (locality, leverage, tests) | Strength |
|---|---|---|---|---|---|

Strength is `Strong`, `Worth exploring` or `Speculative`. A candidate that
contradicts an ADR appears only when the friction justifies reopening it, marked
with the ADR number and the reason. Do not list refactors an ADR forbids just
because they are possible.

When the user wants pictures, write one self-contained HTML report with a
before/after diagram per candidate and a final "start here" pick, to
`<repo>/.tmp/deepen-<date>.html` (the repo's scratch directory), styled with the
`html-style` skill when it is available. Report the absolute path.

Done when the table is shown. Ask which candidate to explore, then stop.

## 4. Hand the pick to a grilling

Recommend the `interview` skill for the chosen candidate. It runs `grill-me` and
`domain-modeling` over the open decisions: constraints, dependencies, the shape of
the deepened module, what sits behind the seam, which tests survive. Naming a new
concept updates the glossary there.

- Alternative interfaces for the deepened module: recommend the design-it-twice
  procedure in [DESIGN-IT-TWICE.md](./DESIGN-IT-TWICE.md).
- How to deepen the picked cluster given its dependencies (in-process,
  local-substitutable, remote but owned, true external) and how its tests change:
  [DEEPENING.md](./DEEPENING.md).
- The user rejects a candidate for a load-bearing reason a future survey would
  need: offer to record an ADR. Skip ephemeral reasons ("not worth it right now")
  and self-evident ones.

Done when the user has picked a candidate and the next skill is named, or has
rejected all of them with their reasons recorded.
