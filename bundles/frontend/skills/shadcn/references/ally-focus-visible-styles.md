---
title: Preserve Focus Visible Styles for Keyboard Navigation
impact: MEDIUM-HIGH
impactDescription: required for keyboard users to track focus position
tags: ally, focus, keyboard, navigation, ring
---

## Preserve Focus Visible Styles for Keyboard Navigation

Never remove focus ring styles. Keyboard users rely on visible focus indicators to navigate the interface. shadcn/ui components include focus-visible styles by default.

**Incorrect (focus styles removed):**

```tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center outline-none", // Removed focus ring, nothing replaces it
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
      },
    },
  }
)
// Keyboard users cannot see which button is focused
```

**Correct (focus-visible styles preserved):**

```tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
      },
    },
  }
)
```

Tailwind v4 notes: `ring` utilities now default to 1px (use `ring-3` for the shadcn width), and the old `outline-none` behavior is `outline-hidden` (it keeps a transparent outline for forced-colors mode). Either is fine when a `focus-visible:ring-*` replaces it.

**Custom focus styles (if needed):**

```tsx
// Still visible, but customized
<Button className="focus-visible:ring-brand/50 focus-visible:border-brand">
  Custom Focus
</Button>
```

**Why focus-visible (not focus):**

- `focus`: Shows ring on mouse click too
- `focus-visible`: Only shows ring for keyboard navigation

Reference: [WCAG Focus Visible](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html)
