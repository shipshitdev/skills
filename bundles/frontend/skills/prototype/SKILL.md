---
name: prototype
description: Builds a throwaway prototype to answer one design question about state logic or UI look. Use when sanity-checking a state model or exploring what a UI should look like.
license: MIT
metadata:
  version: "2.2.2"
  tags: "prototype, design, ui, state-machine, throwaway"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d
  last_synced: "2026-10-06"
  license: MIT
when_to_use: "spike, mock up, try variants, throwaway"
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides
the shape.

## Contract

Inputs:

- One design question (state/logic, or how it should look)
- The surrounding module or page when one exists

Outputs:

- A runnable prototype (single HTML file, or UI variants on one route)
- The captured answer (verdict + question it settled), pointed at from the
  implementation issue

Creates/Modifies:

- Prototype files next to the real module or page, named so they read as
  prototypes
- A throwaway `prototype/<name>` branch when capturing the primary source

External Side Effects:

- Local files. Git branch for capture. No production deploys.

Confirmation Required:

- Before committing the throwaway branch
- Before folding a validated decision into production code

Delegates To:

- None. Distinct from `artifacts-builder` (production artifacts) and
  `theme-factory` (visual theme systems).

## Pick a branch

Identify which question is being answered — from the user's prompt, the
surrounding code, or by asking:

- **"Does this logic / state model feel right?"** → [references/LOGIC.md](references/LOGIC.md).
  A single shareable HTML file — free-play buttons plus tabbed guided walkthroughs.
- **"What should this look like?"** → [references/UI.md](references/UI.md).
  Several radically different UI variations on a single route, switchable via a
  URL search param and a floating bottom bar.

The two branches produce very different artifacts. Getting this wrong wastes the
whole prototype. If the question is genuinely ambiguous and the user is not
reachable, default to whichever branch better matches the surrounding code (a
backend module → logic; a page or component → UI) and state the assumption at
the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype
   close to where it will actually be used. Name it so a casual reader can see it
   is a prototype, not production.
2. **Trivial to run.** A UI prototype starts from one command in the project's
   task runner. A logic demo is a single HTML file the user double-clicks.
3. **No persistence by default.** State lives in memory. Persistence is the thing
   the prototype is *checking*, not something it should depend on.
4. **Skip the polish.** No tests, no error handling beyond what makes it
   runnable, no abstractions. Learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch
   (UI), print or render the full relevant state.
6. **Capture it when done.** Fold any validated decision into the real code, then
   capture the prototype itself as a **primary source**: commit it to a throwaway
   branch, out of main, and leave a context pointer to that branch on the
   implementation issue. Capture the answer too. The main branch keeps only the
   validated decision.
