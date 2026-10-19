---
name: accessibility
description: Applies WCAG 2.1 AA to web UI and fixes failures. Use when building or reviewing components for a11y, ARIA, keyboard navigation, focus traps, or contrast.
metadata:
  version: "2.2.4"
  tags: "accessibility, a11y, wcag, aria, keyboard-navigation, screen-reader, inclusive-design"
when_to_use: "screen readers, semantic HTML"
---

# Accessibility (a11y)

Use when creating or reviewing UI components, implementing interactive elements (buttons, forms, modals), adding keyboard navigation, reviewing color contrast, testing with screen readers, auditing pages, or adding ARIA attributes.

## Workflow

1. Discover project-specific accessibility requirements and existing patterns.
2. Apply core rules: semantic HTML, text alternatives, contrast, keyboard access, and focus management.
3. Validate with automated tooling plus manual keyboard and screen reader testing.
4. Document issues and fixes with examples.

## WCAG principles

- Perceivable: text alternatives, contrast, responsive support.
- Operable: keyboard access, focus management, timing.
- Understandable: clear language, predictable behavior.
- Robust: valid HTML and ARIA usage.

## References

- [Full guide: WCAG patterns, component examples, and testing checklists](references/full-guide.md)

## Related

- `audit`: a scored 0-4 sweep across accessibility, performance, theming, responsive design, and implementation integrity, for when no single dimension is named.
