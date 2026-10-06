---
title: Define Custom Design Tokens in CSS with @theme inline
impact: HIGH
impactDescription: maintains design system consistency
tags: style, tailwind-v4, theme, design-tokens, css-variables, configuration
---

## Define Custom Design Tokens in CSS with @theme inline

Add brand colors and custom design tokens in your global CSS rather than using arbitrary values. Tailwind v4 is CSS-first: there is no `tailwind.config.*` and no `theme.extend`. Define the token under `:root` and `.dark`, then expose it to Tailwind with `@theme inline`. This creates reusable utilities and keeps light and dark values in one place.

**Incorrect (arbitrary values scattered):**

```tsx
function BrandedCard() {
  return (
    <Card className="bg-[#1a365d] border-[#2a4a7f]">
      <CardHeader>
        <CardTitle className="text-[#e2e8f0]">
          {/* Arbitrary values: no shared token, no dark mode, hard to maintain */}
          Dashboard
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-[#a0aec0]">Welcome to your dashboard</p>
      </CardContent>
    </Card>
  )
}
```

**Incorrect (Tailwind v3 config, ignored by v4 and rejected by shadcn with an empty `tailwind.config`):**

```js
// tailwind.config.js
module.exports = {
  theme: { extend: { colors: { brand: { 500: "#1a365d" } } } },
}
```

**Correct (tokens in globals.css):**

```css
/* globals.css */
:root {
  --brand: oklch(0.32 0.07 255);
  --brand-foreground: oklch(0.93 0.01 255);
  --brand-muted: oklch(0.72 0.02 255);
}

.dark {
  --brand: oklch(0.45 0.1 255);
  --brand-foreground: oklch(0.97 0.01 255);
  --brand-muted: oklch(0.78 0.02 255);
}

@theme inline {
  --color-brand: var(--brand);
  --color-brand-foreground: var(--brand-foreground);
  --color-brand-muted: var(--brand-muted);
}
```

```tsx
function BrandedCard() {
  return (
    <Card className="bg-brand border-brand/60">
      <CardHeader>
        <CardTitle className="text-brand-foreground">
          {/* Utilities generated from the tokens, light and dark handled */}
          Dashboard
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-brand-muted">Welcome to your dashboard</p>
      </CardContent>
    </Card>
  )
}
```

**Benefits of CSS-first tokens:**

- Utilities (`bg-brand`, `text-brand-foreground`) and IDE autocomplete come from the `--color-*` namespace
- Single source of truth for brand colors, with dark mode via `.dark` overrides
- Works with opacity modifiers (`bg-brand/50`)
- Tokens are plain CSS variables, usable from JavaScript and inline styles

Reference: [shadcn/ui Theming: Adding New Tokens](https://ui.shadcn.com/docs/theming) and [Tailwind Theme variables](https://tailwindcss.com/docs/theme)
