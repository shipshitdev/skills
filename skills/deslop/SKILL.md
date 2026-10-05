---
name: deslop
description: "Strips AI slop from code, product, and prose: console logs, any types, dead comments, filler copy, dead buttons. Use when asked to unslop, clean AI code, or polish before shipping."
argument-hint: "[ui | prose | --changed | all | dry-run | --product]"
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.2"
  tags: "code-quality, cleanup, ai-artifacts, product-polish, prose, maintenance"
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "--product, ui, prose, dry-run"
---

# Deslop

AI-assisted development leaves three kinds of slop. **Code slop** compiles but
reads as machine-written. **Product slop** ships but feels unfinished to a
paying customer. **Prose slop** is writing with AI tells: puffery, em-dash
habits, chatbot phrases, voiceless neutrality. This skill removes all three.
Code slop is the default. `--product` adds the product pass. `prose` runs the
writing pass. `ui` runs only the design-system pass.

Edits and removes code, so it runs behind a confirmation gate and prefers the
branch diff. For a read-only pass that only flags, use `structural-review` /
`/review`. For a layered doc standard (Diátaxis, STE, Global English), use
`technical-writing` and then apply the prose catalog here.

Other skills that need the prose catalog point at
[references/prose-slop.md](references/prose-slop.md). They do not fire this
skill.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A package, repo, or prose surface to clean; optional scope (`--changed`,
  `all`, `dry-run`) and dimension (`--product`, `ui`, `prose`).

Outputs:

- Applied edits (or, in `dry-run`, a grouped report of what would change), plus
  a short count of artifacts removed by type.

Creates/Modifies:

- Edits source files or named prose. Never deletes entry points, configs, or
  READMEs.

External Side Effects:

- None beyond local file edits. Runs type-check and tests after code edits.

Confirmation Required:

- Before sweeping the whole tree (`all`) or rewriting product copy whose intent
  is ambiguous.

Delegates To:

- `polish` for the final micro-detail pass after the structural slop is gone.
- `refactor-code` when a fix is a real refactor, not a mechanical strip.
- `technical-writing` when the ask is a docs, RFC, README, PR, or commit
  standard rather than a slop strip.

## Code slop (default)

Remove, matching the surrounding file's existing style:

1. **Console statements** → the project logger.
2. **`any` types** → real types or `unknown` + a type guard.
3. **Unused imports / variables** → delete.
4. **Commented-out code** → delete (git remembers it).
5. **Debug / temporary code** → delete leftover TODO/FIXME debug lines.
6. **Redundant comments** — remove those that restate *what*; keep those that
   explain *why*.
7. **Needless defensive checks** — drop try-catch and null guards on trusted
   internal paths that cannot fail; keep guards on real external boundaries.
8. **Over-nesting** — collapse deep if/else pyramids into early returns.

## Prose slop (`prose`)

When the first argument is `prose`, or when the target is a reply, README,
RFC, PR description, commit message, or other writing surface, apply
[references/prose-slop.md](references/prose-slop.md).

1. Scan for the 33 patterns.
2. Rewrite. Preserve meaning. Match intended tone.
3. Add soul: opinions, varied rhythm, specific facts.
4. Self-audit: "What makes this obviously AI generated?" Fix remaining tells.

`--product` copy cleanup also runs this catalog. Do not invent product voice
when the intended copy is unclear; flag it.

## Product slop (`--product`)

The layer that decides whether an app feels finished. See
[references/product-slop.md](references/product-slop.md) for the full Incorrect
→ Correct catalog; the three families:

- **Copy** — marketing filler, generic AI phrasing, empty-states and error
  messages that say nothing useful. Run the prose catalog on every string.
- **UI** — the untouched-shadcn-plus-purple-gradient look, inconsistent
  spacing/radius, loading and error states left unstyled or absent.
- **UX** — buttons wired to nothing, flows that dead-end, placeholder pages
  behind real-looking nav, forms with no validation or success feedback.

Product slop needs judgment, not just deletion. Flag anything ambiguous rather
than guessing at intended copy or behavior.

## UI slop (`ui`)

When the first argument is `ui`, run only the UI pass. Do not run the code
cleanup workflow first.

Do not encode component-specific styling rules in this skill. Derive them from
the target project.

Before judging taste, inspect the local source of truth:

- Design docs, tokens, theme files, CSS variables, Tailwind config, or equivalent.
- Shared UI primitives such as cards, buttons, inputs, dialogs, tables, tabs,
  nav, badges, tooltips, menus, and loading states.
- Three nearby good examples in the same app or package.
- The target screen/component code and rendered output when available.

Create a short working inventory:

- Approved tokens and spacing/radius/shadow patterns.
- Shared primitives and their variants.
- UI-role map for the audited surface: primitive, documented recipe, or missing.
- Local examples that already look production-ready.
- Target files and routes affected.

For each UI role present on the audited surface, identify whether the project
has a shared primitive or documented recipe:

- Surface, card, panel.
- Button or action.
- Link or navigation.
- Input, select, textarea.
- Checkbox, radio, switch.
- Badge or status.
- Modal, dialog, drawer, popover, tooltip.
- Table, list, grid.
- Tabs or segmented controls.
- Empty, loading, error states.
- App shell, navigation, layout sections.

If a primitive exists:

- Use it instead of raw HTML, copied markup, or local styling.
- Use only its public props, variants, slots, and documented composition
  patterns.
- Do not override its core visual contract from call sites: background, border,
  radius, shadow, typography, spacing, focus, disabled, loading, or state
  styling.
- If the needed variant does not exist, add a named variant to the primitive
  only when the need is clear and reusable. Otherwise defer with a finding.

If no primitive exists:

- Follow the documented design recipe or the strongest nearby local pattern.
- If the same recipe appears repeatedly, recommend extracting a primitive or
  named variant.
- Do not invent a one-off visual treatment unless the user explicitly requested
  a bespoke design.

Raw semantic HTML is fine for document structure and prose. Raw HTML is not
fine when it is acting as a design-system control or surface.

Fix objective design-system drift before subjective taste. Keep changes scoped
to the audited surface and defer product-judgment calls with a concrete finding
instead of inventing intent.

## Workflow

1. **Route mode** — `ui` runs the UI pass and stops. `prose` runs the prose
   catalog and stops. `--product` adds product + prose after code slop.
2. **Detect structure** — monorepo vs single package
   (`ls packages/ 2>/dev/null`). Process each package separately.
3. **Scope** — in `--changed`, limit edits to the branch diff:

   ```bash
   BASE="$(git merge-base HEAD origin/HEAD 2>/dev/null || git merge-base HEAD main 2>/dev/null || git merge-base HEAD master)"
   git diff --name-only "$BASE"..HEAD    # files this branch touched
   ```

   Touch only those files/hunks; do not clean pre-existing slop elsewhere in
   this mode.
4. **Strip** by the categories above.
5. **Verify** — a code change must still build and pass:

   ```bash
   bun run type-check || bunx tsc --noEmit
   bun run test
   ```

6. **Document** — log packages cleaned and per-type counts in the current
   repository's session log when one exists.

## Modes

- **default** — code slop, current package, edits applied.
- **`ui`** — run the UI/design-system primitive pass.
- **`prose`** — run the writing-tell catalog only.
- **`--changed`** — only the files/hunks this branch introduced (safest for a PR).
- **`--product`** — add the product-slop pass (copy/UI/UX) and the prose catalog.
- **`all`** — sweep every package in a monorepo, each processed separately.
- **`dry-run`** — detect only; report every artifact grouped by type with
  counts, edit nothing. Combines with any scope.

## Anti-Patterns

- **Cleaning the whole tree when a branch scope was meant** — `--changed`
  keeps a PR reviewable; whole-tree edits need confirmation.
- **Deleting side-effect imports** (CSS, polyfills) or critical files
  (README, configs, entry points).
- **Removing a "why" comment** because it looks redundant — only
  *what*-restating comments go.
- **Guessing at product copy or intended behavior** — flag ambiguous product
  slop for the user instead of inventing a fix.
- **Rewriting logic under the banner of cleanup** — a behavior change is a
  refactor (`refactor-code`), not deslop.
- **Leaving voiceless prose after the strip** — sterile writing is still slop.

## Deslop procedure

Read [deslop procedure](references/deslop-procedure.md) for the code mode only.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.

## Unslop procedure

Read [unslop procedure](references/unslop-procedure.md) for prose mode or the prose portion of product cleanup only.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
