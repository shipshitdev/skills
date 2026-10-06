---
title: Enable CSS Variables for Consistent Theming
impact: CRITICAL
impactDescription: enables dark mode and design system consistency
tags: setup, css-variables, theming, tailwind-v4, theme-inline, configuration
---

## Enable CSS Variables for Consistent Theming

Setting `cssVariables: true` in components.json enables the CSS variable-based theming system. Without this, dark mode and theme customization fail.

**Incorrect (utility classes without variables):**

```json
// components.json
{
  "tailwind": {
    "cssVariables": false
  }
}
```

```css
/* Generated component uses hardcoded colors */
.button {
  @apply bg-zinc-900 text-zinc-50;
}
/* Dark mode requires separate class overrides for every color */
```

**Correct (CSS variables enabled):**

```json
// components.json
{
  "tailwind": {
    "cssVariables": true,
    "baseColor": "neutral"
  }
}
```

```css
/* globals.css - single source of truth */
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";

@custom-variant dark (&:is(.dark *));

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
}

/* Expose each variable as a Tailwind utility (bg-background, text-primary, ...) */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
}
```

`@theme inline` makes each utility reference `var(--background)` directly, so the value resolves where the class is used and `.dark` overrides (including nested `.dark` containers) take effect. A plain `@theme` resolves the reference once on `:root`.

Components automatically adapt to theme changes via CSS variables.

Reference: [shadcn/ui Theming](https://ui.shadcn.com/docs/theming)
