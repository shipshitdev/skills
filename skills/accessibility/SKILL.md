---
name: accessibility
description: Applies WCAG 2.1 AA to web UI and fixes failures. Use when building or reviewing components for a11y, ARIA, keyboard navigation, focus traps, or contrast.
metadata:
  version: "2.2.4"
  tags: "accessibility, a11y, wcag, aria, keyboard-navigation, screen-reader, inclusive-design"
when_to_use: "screen readers, semantic HTML"
---

# Accessibility (a11y) Skill

## When to Use

Use when you're:

- Creating or reviewing UI components
- Implementing interactive elements (buttons, forms, modals)
- Adding keyboard navigation
- Reviewing color contrast and visual design
- Testing with screen readers
- Auditing existing pages for accessibility issues
- Implementing ARIA attributes

## Quick Workflow

1. Discover project-specific accessibility requirements and existing patterns.
2. Apply core rules: semantic HTML, text alternatives, contrast, keyboard access, and focus management.
3. Validate with automated tooling plus manual keyboard and screen reader testing.
4. Document issues and fixes with examples.

## WCAG Principles

- Perceivable: text alternatives, contrast, responsive support.
- Operable: keyboard access, focus management, timing.
- Understandable: clear language, predictable behavior.
- Robust: valid HTML and ARIA usage.

## References

- [Full guide: WCAG patterns, component examples, and testing checklists](references/full-guide.md)

## Related

- `audit` — a scored 0-4 sweep across accessibility, performance, theming, responsive design, and anti-patterns when no single dimension is named.
- `design-consistency-auditor` — token drift, hardcoded colors, and design-system divergence.
