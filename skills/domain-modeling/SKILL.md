---
name: domain-modeling
description: Builds and sharpens a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR.
license: MIT
metadata:
  version: "2.2.4"
  tags: "domain, glossary, context, adr, ddd"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9
  last_synced: "2026-10-05"
  license: MIT
when_to_use: "glossary, ubiquitous language"
---

# Domain Modeling

Actively build and sharpen the project's domain model while designing. Challenge terms, invent edge-case scenarios, and write the glossary and decisions down the moment they crystallise.

Merely reading the glossary for vocabulary is not this skill; any skill can do that. This skill is for changing the model, not just consuming it.

**Glossary file name.** This skill writes `CONTEXT.md` (and `CONTEXT-MAP.md` for multiple contexts). A repo that already uses `GLOSSARY.md` / `GLOSSARY-MAP.md` keeps that name: read and update whichever exists and never create the second beside it. A repo with neither gets `CONTEXT.md`. Pick once; below, **the glossary** means the selected file and **the map** its `-MAP` companion.

## Contract

Inputs:

- A term, relationship, or decision under discussion
- Existing glossary (`CONTEXT.md` / `CONTEXT-MAP.md`, or `GLOSSARY.md` / `GLOSSARY-MAP.md`) and `docs/adr/` when present
- `docs/agents/domain.md` when `setup-agent-routing` has already configured layout

Outputs:

- Updated glossary entries in the repo's glossary file
- Optional ADR when the three-gate filter passes

Creates/Modifies:

- The glossary file (or a per-context one listed in the map file)
- `docs/adr/NNNN-slug.md` when an ADR is warranted
- Directories created lazily — only when there is something to write

External Side Effects:

- Local file writes only. No tracker writes.

Confirmation Required:

- Before creating the first glossary file in a repo that had none
- Before writing an ADR

Delegates To:

- None. `grill-me` and `interview` invoke this skill when a term crystallises.

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

If the map exists at the root, the repo has multiple contexts and the map points to where each lives. Prefer a layout already recorded in `docs/agents/domain.md`. Create the glossary when the first term is resolved and `docs/adr/` when the first ADR is needed.

## During the session

- **Challenge against the glossary.** When the user's term conflicts with the glossary, say so immediately: "The glossary defines 'cancellation' as X, but this sounds like Y. Which is it?"
- **Sharpen fuzzy language.** For vague or overloaded terms, propose a precise canonical term: "'Account': Customer or User? Those are different things."
- **Discuss concrete scenarios.** Stress-test relationships with invented edge cases that force precise boundaries between concepts.
- **Cross-reference with code.** When the user states how something works, check the code. Surface contradictions: "The code cancels entire Orders, but you said partial cancellation is possible. Which is right?"
- **Update the glossary inline.** Update it the moment a term is resolved; do not batch. Use the format in [references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md). The glossary holds terms and nothing else: no implementation details, scratch notes or specs.
- **Offer ADRs sparingly.** Only when all three hold: (1) hard to reverse, (2) surprising without context, (3) the result of a real trade-off between genuine alternatives. If any is missing, skip the ADR. Use the format in [references/ADR-FORMAT.md](references/ADR-FORMAT.md).
