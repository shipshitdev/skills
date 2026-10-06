---
name: architect
description: Sketches types, signatures, and module structure before code, then guides implementation. Use for architect this, or non-trivial work where coding first locks in the wrong shape.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.3"
  tags: "architecture, design, types, modules"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/architect/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "design this first, module shape"
---

# Architect

Design before implementing. Sketch types, function signatures, class
shapes, and module boundaries with `not implemented` bodies. Synthesize
across parallel candidates, then fill in code against the chosen sketch.

Companion to `codebase-design`, which owns deep-module vocabulary. This
skill owns the pre-implementation sketch loop.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A change that crosses a function boundary, or non-trivial work whose
  shape is still unset

Outputs:

- A synthesized design package: caller usage first, then types,
  signatures, module map, and rationale
- Implementation against that sketch, or a scrap-and-redesign

Creates/Modifies:

- Design artifacts and, after agree, production code

External Side Effects:

- None beyond local files unless a later playbook opens a PR

Confirmation Required:

- Opt-in checkpoint when the invoker asks to see the sketch first

Delegates To:

- `how` for grounding, `why` when ownership or layering is the
  constraint, `arena` for candidate sketches, `interrogate` when the
  design is contested

## Phases

Open a todo list with one entry per phase: Ground, Sketch, Agree,
Implement, Scrap.

### A. Ground

Run `how` over every system the new code touches. If the design
redefines ownership or layering, also run `why` on the existing shape.
Skip only when the work is genuinely greenfield.

### B. Sketch

Run `arena` with the design-sketch task. Each candidate produces a
package shaped per
[references/rationale-template.md](references/rationale-template.md)
using [references/runner-prompt.md](references/runner-prompt.md).

Require at least two structurally distinct candidates. Screen every
candidate against
[references/design-red-flags.md](references/design-red-flags.md).
Prefer the design that hides more complexity behind a smaller public
surface.

### C. Agree

Default: proceed to implementation. Opt in to a checkpoint when the
invoker asks to see the sketch first. Human pushback is Phase A
evidence. Re-ground and re-run Phase B.

### D. Implement

Replace `not implemented` bodies. Deviations from the sketch are
signal. Surface them. Do not bolt them on silently.

### E. Scrap

If implementation keeps producing the same shape of friction, throw the
sketch out. Re-run `how` over what was built. Redesign as if the new
constraints were day-one assumptions. Subtract before adding. Return to
Phase B.

## Architect procedure

Read [architect procedure](references/architect-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
