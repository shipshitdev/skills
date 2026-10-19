---
name: shape
description: Plan the UX and UI for a feature before writing code. Produces a design brief that guides implementation.
user-invocable: true
disable-model-invocation: true
argument-hint: "[feature to shape]"
metadata:
  version: "2.2.4"
  tags: "ux, planning, design-brief"
  source: https://github.com/pbakaus/impeccable/blob/main/skill/reference/shape.md
  upstream_version: skill-v4.5.0
  upstream_latest: skill-v4.5.0
  last_synced: "2026-10-06"
  license: Apache-2.0
when_to_use: "shape this, design brief, plan the UX, plan the UI, before writing UI code, /shape"
---

# Shape

Shape the UX and UI for a feature before any code is written. The output is a **design brief**: a structured artifact that guides implementation through discovery, not guesswork.

- **Scope:** design planning only. Write no code.
- **Output:** a design brief that can be handed to any implementation skill or approach.
- **Handoff:** after the brief is confirmed, recommend an implementation skill; do not invoke another user-invoked skill yourself.

## Context gathering

Before the interview, ground yourself in the project so the brief reflects what already exists:

- **Design context:** if the repo carries any of `PRODUCT.md`, `DESIGN.md`, `.impeccable.md`, or a `## Design Context` block in `.github/copilot-instructions.md`, read it. Skip silently if none exist.
- **Existing system:** read the established design system (CSS / tokens / theme and one representative component or page) to learn the conventions in play. Use what is there; branch out only when the UX wins.
- **Register:** decide whether design *is* the product (marketing, landing, portfolio: identity and boldness lead) or *serves* the product (app, dashboard, tool: clarity and restraint lead). This frames every direction choice below.

## Phase 1: Discovery interview

Write no code and make no design decisions in this phase. Understand the feature deeply enough to make excellent design decisions later.

Run an interview skill (e.g. `grill-me`) if available; otherwise interview the user directly, in rounds, with a recommended answer for each question. Seed the design tree with these branches so the interview covers them:

- **Purpose and context:** what it is for, who specifically uses it, what success looks like, the user's state of mind
- **Content and data:** what is shown or collected, realistic ranges, empty/error/first-time/power-user cases, what is dynamic
- **Design goals:** the single most important user action, how it should feel, existing product patterns, reference examples
- **Scope:** fidelity, breadth, interactivity, named target and what remains untouched
- **Constraints:** technical, content, mobile, accessibility beyond WCAG AA
- **Anti-goals:** wrong directions and the biggest risk of getting this wrong

Do not ask what the repo already answers.

## Phase 2: Design brief

Synthesize everything into a design brief and present it for confirmation before considering the work complete.

Use three to five bullets when the task is settled; use the full structure for ambiguous or multi-screen work. Include scope, realistic ranges, required media roles, and decisions a builder must not invent. Resolve consequential open decisions before handoff; do not leave them for implementation.

### Brief structure

1. **Feature summary** (2-3 sentences): what it is, who it is for, what it must accomplish.
2. **Primary user action:** the single most important thing a user should do or understand here.
3. **Design direction:** how it should feel and which aesthetic approach fits. Reference the project's design context (if present) and explain how this feature expresses it.
4. **Layout strategy:** high-level spatial approach: what gets emphasis, what is secondary, how information flows. Describe hierarchy and rhythm, not specific CSS.
5. **Key states:** every state needed (default, empty, loading, error, success, edge cases) and what the user needs to see and feel in each.
6. **Interaction model:** what happens on click, hover, scroll; what feedback users get; the flow from entry to completion.
7. **Content requirements:** copy, labels, empty-state and error messages, microcopy; any dynamic content and its realistic ranges.
8. **Recommended references:** which reference files or documentation would help most during implementation (e.g. spatial design for complex layouts, motion for animated features, interaction design for form-heavy features).
9. **Open questions:** anything unresolved that blocks handoff. Resolve with the user before implementation; a confirmed brief does not silently delegate design decisions.

## Finish

Ask the user directly about anything you cannot infer. Get explicit confirmation of the brief before finishing; if the user disagrees with any part, revisit the relevant discovery questions. Once confirmed, the brief is complete and can go to any implementation skill or approach.
