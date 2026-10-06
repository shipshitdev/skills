---
title: Support Dark Mode with CSS Variables
impact: HIGH
impactDescription: provides user preference compliance and reduces eye strain
tags: style, dark-mode, theming, css-variables, custom-variant, tailwind-v4, accessibility
---

## Support Dark Mode with CSS Variables

Use the shadcn/ui dark mode pattern with CSS variables. Define both light and dark values; components automatically adapt.

**Incorrect (hardcoded mode-specific styles):**

```tsx
function NotificationCard({ message }: { message: string }) {
  return (
    <Card className="bg-white text-gray-900 border-gray-200">
      {/* No dark mode support - harsh white in dark environments */}
      <CardContent className="p-4">
        <p className="text-gray-600">{message}</p>
      </CardContent>
    </Card>
  )
}
```

**Correct (CSS variables with dark mode support):**

```css
/* globals.css */
@import "tailwindcss";
@custom-variant dark (&:is(.dark *));

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
}
```

`@custom-variant dark (&:is(.dark *));` makes the `dark:` variant follow the `.dark` class instead of the OS setting. Toggle the class on `<html>`.

```tsx
function NotificationCard({ message }: { message: string }) {
  return (
    <Card className="bg-card text-card-foreground border-border">
      {/* Automatically adapts to light/dark mode */}
      <CardContent className="p-4">
        <p className="text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  )
}
```

**Theme toggle implementation (Next.js with next-themes; Vite uses a small ThemeProvider that toggles the `dark` class, see the shadcn dark mode guide):**

```tsx
import { useTheme } from "next-themes"

function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button variant="outline" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      <SunIcon className="size-4 rotate-0 scale-100 dark:-rotate-90 dark:scale-0" />
      <MoonIcon className="absolute size-4 rotate-90 scale-0 dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

Reference: [shadcn/ui Dark Mode](https://ui.shadcn.com/docs/dark-mode)
