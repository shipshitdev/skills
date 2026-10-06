---
name: shape
description: Plan the UX and UI for a feature before writing code. Produces a design brief that guides implementation.
user-invocable: true
disable-model-invocation: true
argument-hint: "[feature to shape]"
metadata:
  version: "2.2.2"
  tags: "ux, planning, design-brief"
  source: https://github.com/pbakaus/impeccable/blob/main/skill/reference/shape.md
  upstream_version: skill-v3.1.1
  upstream_latest: skill-v4.5.0
  last_synced: "2026-06-12"
  license: Apache-2.0
when_to_use: "shape this, design brief, plan the UX, plan the UI, before writing UI code, /shape"
---

Shape the UX and UI for a feature before any code is written. This skill produces a **design brief**: a structured artifact that guides implementation through discovery, not guesswork.

**Scope**: Design planning only. This skill does NOT write code. It produces the thinking that makes code good.

**Output**: A design brief that can be handed off to any implementation skill.

Delegates To: `grill-me` for Phase 1. Recommend an implementation skill after the brief is confirmed; do not invoke another user-invoked skill.

## Context Gathering

Before the interview, ground yourself in the project so the brief reflects what already exists:

- **Design context** — if the repo carries any of `PRODUCT.md`, `DESIGN.md`, `.impeccable.md`, or a `## Design Context` block in `.github/copilot-instructions.md`, read it. Skip silently if none exist.
- **Existing system** — read the established design system (CSS / tokens / theme and one representative component or page) to learn the conventions in play. Use what's there; branch out only when the UX wins.
- **Register** — decide whether design *is* the product (marketing, landing, portfolio → identity and boldness lead) or design *serves* the product (app, dashboard, tool → clarity and restraint lead). This frames every direction choice below.

## Phase 1: Discovery Interview

Write no code and make no design decisions in this phase. Understand the feature deeply enough to make excellent design decisions later.

Run the `grill-me` skill. Seed the design tree with these branches so the **frontier** covers them:

- **Purpose and context** — what this is for, who specifically uses it, success, user state of mind
- **Content and data** — what is shown or collected, realistic ranges, empty/error/first-time/power-user cases, what is dynamic
- **Design goals** — the single most important user action, how it should feel, existing product patterns, reference examples
- **Constraints** — technical, content, mobile, accessibility beyond WCAG AA
- **Anti-goals** — wrong directions and the biggest risk of getting this wrong

Facts that the repo already answers stay off the frontier. `grill-me` asks the rest in rounds with recommended answers.

## Phase 2: Design Brief

After the interview, synthesize everything into a structured design brief. Present it to the user for confirmation before considering this skill complete.

### Brief Structure

**1. Feature Summary** (2-3 sentences)
What this is, who it's for, what it needs to accomplish.

**2. Primary User Action**
The single most important thing a user should do or understand here.

**3. Design Direction**
How this should feel. What aesthetic approach fits. Reference the project's design context from `.impeccable.md` or `.github/copilot-instructions.md` (if present) and explain how this feature should express it.

**4. Layout Strategy**
High-level spatial approach: what gets emphasis, what's secondary, how information flows. Describe the visual hierarchy and rhythm, not specific CSS.

**5. Key States**
List every state the feature needs: default, empty, loading, error, success, edge cases. For each, note what the user needs to see and feel.

**6. Interaction Model**
How users interact with this feature. What happens on click, hover, scroll? What feedback do they get? What's the flow from entry to completion?

**7. Content Requirements**
What copy, labels, empty state messages, error messages, and microcopy are needed. Note any dynamic content and its realistic ranges.

**8. Recommended References**
Based on the brief, list which reference files or documentation would be most valuable during implementation (e.g., spatial design guidance for complex layouts, motion design for animated features, interaction design for form-heavy features).

**9. Open Questions**
Anything unresolved that the implementer should resolve during build.

---

ask the user directly to clarify what you cannot infer. Get explicit confirmation of the brief before finishing. If the user disagrees with any part, revisit the relevant discovery questions.

Once confirmed, the brief is complete. The user can now hand it to any implementation skill or approach.
