---
name: design-consistency-auditor
description: "Hunts design-token drift in frontends: hardcoded colors, off-scale spacing, one-off classes duplicating components. Use when auditing styling consistency or design debt."
metadata:
  version: "2.2.4"
  tags: "design, ux, ui, consistency, design-tokens, design-debt, tailwind"
when_to_use: "hardcoded hex, palette usage"
---

# Design Consistency Auditor

Before auditing, discover the project's frontend structure from its documentation and code (design docs, tokens, theme files, Tailwind config, shared UI components).

Ensures:

- Color palettes are used through semantic tokens
- Spacing stays on the project's scale
- Components look consistent across screens
- The design system is applied, not duplicated
- No design debt accumulates

## When to use

- Auditing design-token consistency across apps
- Reviewing palette usage and hunting hardcoded hex values
- Checking UI patterns for screen-to-screen divergence
- Spotting one-off classes that duplicate a design-system component
- Reviewing new features against established design standards

Accessibility conformance (WCAG, ARIA, keyboard access, contrast) is a separate pass; use an accessibility skill if available. For a scored sweep across accessibility, performance, theming, responsive design and anti-patterns when no single dimension is named, use the `audit` skill.

## Quick reference

**Color.** DO use semantic tokens (for shadcn: `bg-background`, `bg-card`, `bg-primary`, `text-muted-foreground`, `border-border`). DON'T hardcode hex (`#000000`) or arbitrary values (`bg-[#123456]`).

**Components.** Find the project's real class names and components before auditing; do not assume a naming convention. Look for: cards (shadcn `Card` or the project's own), app shells/layouts, modals/dialogs, inputs, and button variants (primary, secondary, ghost).

**Spacing.** DO use the Tailwind scale (`p-4`, `m-6`, `gap-4`). DON'T use arbitrary values (`p-[17px]`).

**Accessibility basics to spot-check.** Semantic HTML (`<button>`, `<nav>`, `<main>`), ARIA labels on interactive elements, 4.5:1 text contrast and 3:1 for UI, visible focus states (`focus:outline-none focus:ring-2 focus:ring-primary`).

**Responsive.** Mobile-first with `sm:`, `md:`, `lg:`, `xl:`; responsive typography such as `text-3xl sm:text-4xl`.

## Audit phases

1. **Color palette:** scan for hardcoded colors; verify theme tokens.
2. **Component patterns:** check cards, buttons and forms use theme classes.
3. **Spacing and layout:** verify a consistent spacing scale.
4. **Typography:** check heading hierarchy and text styles.
5. **Accessibility:** run automated checks and keyboard testing.

## AI slop prevention

Flag generic "AI-generated" aesthetics: Inter/Roboto everywhere, purple gradients on white, predictable layouts without character, safe boring color choices. Push for distinctive, branded design.

## Supporting files

Detailed checklists, examples, report templates and audit commands: `references/full-guide.md`, `examples/quick-audit-checklist.md`, `examples/audit-report-template.md`.
