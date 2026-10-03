---
name: design-consistency-auditor
description: "Hunts design-token drift in frontends: hardcoded colors, off-scale spacing, one-off classes duplicating components. Use when auditing styling consistency or design debt."
metadata:
  version: "2.2.2"
  tags: "design, ux, ui, consistency, design-tokens, design-debt, tailwind"
when_to_use: "hardcoded hex, palette usage"
---

# Design Consistency Auditor

Before auditing, discover the project's frontend structure from documentation.

Ensures:

- Color palettes are used consistently through semantic tokens
- Spacing stays on the project's scale
- Components maintain visual harmony across screens
- The design system is applied instead of duplicated
- No design debt accumulates

## When to Use

- Auditing design-token consistency across apps
- Reviewing color palette usage and hunting hardcoded hex values
- Checking UI/UX patterns for screen-to-screen divergence
- Spotting one-off classes that duplicate a design-system component
- Reviewing new features against the established design standards

Accessibility conformance is a separate pass — use `accessibility` for WCAG, ARIA,
keyboard access, and contrast.

## Quick Reference

### Color Rules

**DO:** Use semantic tokens (`bg-primary`, `text-base-content`, `bg-base-100`)
**DON'T:** Hardcode hex colors (`#000000`) or arbitrary values (`bg-[#123456]`)

### Component Patterns

Discover the project's component class conventions from its design system or existing codebase. Common patterns to look for:

- Cards: project-specific card class or component (e.g. `card`, `.card`, design-system Card component)
- App shells / layouts: project-specific shell wrapper class
- Modals / dialogs: project dialog component pattern
- Inputs: project form input class or component
- Buttons: project button variants (primary, secondary, ghost)

Identify the actual class names from the codebase before auditing — do not assume a specific naming convention.

### Spacing

**DO:** Use Tailwind scale (`p-4`, `m-6`, `gap-4`)
**DON'T:** Use arbitrary values (`p-[17px]`)

### Accessibility

- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- ARIA labels on interactive elements
- 4.5:1 contrast for text, 3:1 for UI
- Focus states: `focus:outline-none focus:ring-2 focus:ring-primary`

### Responsive

- Mobile-first with `sm:`, `md:`, `lg:`, `xl:` modifiers
- Responsive typography: `text-3xl sm:text-4xl`

## Audit Phases

1. **Color Palette** - Scan for hardcoded colors, verify theme tokens
2. **Component Patterns** - Check cards, buttons, forms use theme classes
3. **Spacing & Layout** - Verify consistent spacing scale
4. **Typography** - Check heading hierarchy and text styles
5. **Accessibility** - Run automated checks, keyboard testing

## AI Slop Prevention

Audit for generic "AI-generated" aesthetics:

- Generic fonts (Inter, Roboto everywhere)
- Purple gradients on white
- Predictable layouts without character
- Safe, boring color choices

Push for distinctive, branded designs with personality.

---

**For detailed checklists, examples, reporting templates, and audit commands, see:** `references/full-guide.md`

## Related

- `audit` — a scored 0-4 sweep across accessibility, performance, theming, responsive design, and anti-patterns when no single dimension is named.
- `accessibility` — WCAG 2.1 AA conformance, ARIA, keyboard access, and screen-reader verification.
