---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR.
license: MIT
metadata:
  version: "2.2.2"
  tags: "domain, glossary, context, adr, ddd"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 8b78b531ab96
  last_synced: "2026-08-14"
  license: MIT
---

# Domain Modeling

Actively build and sharpen the project's domain model while designing. Challenge
terms, invent edge-case scenarios, and write the glossary and decisions down the
moment they crystallise.

Reading `CONTEXT.md` for vocabulary is not this skill — that is a one-line habit
any skill can do. This skill is for changing the model, not just consuming it.

## Contract

Inputs:

- A term, relationship, or decision under discussion
- Existing `CONTEXT.md` / `CONTEXT-MAP.md` and `docs/adr/` when present
- `docs/agents/domain.md` when `setup-agent-routing` has already configured layout

Outputs:

- Updated glossary entries in `CONTEXT.md`
- Optional ADR when the three-gate filter passes

Creates/Modifies:

- `CONTEXT.md` (or a per-context `CONTEXT.md` listed in `CONTEXT-MAP.md`)
- `docs/adr/NNNN-slug.md` when an ADR is warranted
- Directories created lazily — only when there is something to write

External Side Effects:

- Local file writes only. No tracker writes.

Confirmation Required:

- Before creating the first `CONTEXT.md` in a repo that had none
- Before writing an ADR

Delegates To:

- None. `grilling` and `interview` invoke this skill when a term crystallises.

## File structure

Most repos have a single context:

```text
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map
points to where each one lives. Prefer the layout already recorded in
`docs/agents/domain.md` when that file exists.

Create files lazily — only when there is something to write. If no `CONTEXT.md`
exists, create one when the first term is resolved. If no `docs/adr/` exists,
create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in
`CONTEXT.md`, call it out immediately. "The glossary defines 'cancellation' as X,
but this sounds like Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term.
"'Account' — Customer or User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific
scenarios. Invent scenarios that probe edge cases and force precise boundaries
between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If they
contradict, surface it: "The code cancels entire Orders, but you just said partial
cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Do not batch these up —
capture them as they happen. Use the format in
[references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md).

`CONTEXT.md` is a glossary and nothing else. Keep implementation details,
scratch notes, and specs out of it.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing later is meaningful
2. **Surprising without context** — a future reader will wonder why it was done
   this way
3. **The result of a real trade-off** — genuine alternatives, picked for specific
   reasons

If any of the three is missing, skip the ADR. Use the format in
[references/ADR-FORMAT.md](references/ADR-FORMAT.md).
