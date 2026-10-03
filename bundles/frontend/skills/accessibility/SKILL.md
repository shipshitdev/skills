---
name: accessibility
description: Applies WCAG 2.1 AA to web UI work and fixes what fails — semantic HTML, ARIA roles and states, keyboard access, focus management, contrast ratios, and screen-reader verification — while a component is being built or reviewed. Use when the user names accessibility, a11y, WCAG, ARIA, keyboard navigation, focus traps, screen readers, or contrast. For a scored multi-dimension quality report, use `audit`; for design-token consistency, use `design-consistency-auditor`.
metadata:
  version: "2.2.2"
  tags: "accessibility, a11y, wcag, aria, keyboard-navigation, screen-reader, inclusive-design"
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
