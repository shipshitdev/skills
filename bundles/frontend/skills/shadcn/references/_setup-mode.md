# Setup Mode: shadcn/ui on Tailwind v4

Install or repair shadcn/ui with the current CSS-first Tailwind v4 setup. Verified against the live shadcn docs (installation, components.json, theming, CLI) and a fresh Next.js and Vite project. The CLI generates all of this; prefer it over hand-written files.

Scope: do only the setup or migration the user asked for. Confirm before overwriting an existing `globals.css`, `components.json` or component files (the CLI asks too; do not pass `--force` or `--overwrite` on existing work without a yes).

## 1. Pick the path

| Situation | Command |
|-----------|---------|
| New Next.js app | `bunx --bun shadcn@latest init -t next -n my-app --base radix --preset nova -y` |
| New Vite app | `bunx --bun shadcn@latest init -t vite -n my-app --base radix --preset nova -y` |
| Existing app with Tailwind v4 and the `@/*` alias | `bunx --bun shadcn@latest init --base radix --preset nova -y` |
| Existing app without Tailwind or the alias | Steps 2 and 3, then the row above |
| Tailwind v3 app | Migrate first (step 7), then the row above |
| Broken or half-configured shadcn | Steps 4 to 6 and the validation checklist (step 8) |

Other templates: `start`, `react-router`, `laravel`, `astro`. `--preset` also skips the interactive prompt. `--base base` selects Base UI instead of Radix (this skill's examples assume Radix). Add components with `bunx --bun shadcn@latest add button card dialog`; preview with `--dry-run` or `view`.

## 2. Tailwind CSS v4 install (existing project)

```bash
# Next.js and other PostCSS frameworks
bun add tailwindcss @tailwindcss/postcss
# Vite
bun add tailwindcss @tailwindcss/vite
```

```js
// postcss.config.mjs (Next.js)
export default { plugins: { "@tailwindcss/postcss": {} } }
```

```ts
// vite.config.ts
import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(import.meta.dirname, "./src") } },
})
```

The CSS entry file starts with `@import "tailwindcss";`. There is no `tailwind.config.*`.

## 3. Path alias

`components.json` aliases must match TypeScript. In Vite projects add `paths` to both `tsconfig.json` and `tsconfig.app.json` (no `baseUrl` needed on TypeScript 6, since `paths` resolves relative to the tsconfig):

```json
{ "compilerOptions": { "paths": { "@/*": ["./src/*"] } } }
```

## 4. Global CSS

`init` writes this for you. The shape (current default neutral theme; full token list in the [theming docs](https://ui.shadcn.com/docs/theming)):

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  /* ...one --color-* line per token (card, popover, secondary, muted, accent,
     destructive, border, input, ring, chart-1..5, sidebar-*) */
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
}

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  /* ... */
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  /* ... */
}

@layer base {
  * { @apply border-border outline-ring/50; }
  body { @apply bg-background text-foreground; }
}
```

Variables live in `:root` and `.dark` as full color values (OKLCH); `@theme inline` maps them to utilities. Do not wrap them in `@layer base` and do not use `hsl(var(--x))` indirection (v3 pattern). Base colors: neutral, stone, zinc, mauve, olive, mist, taupe (`tailwind.baseColor`, fixed at init).

## 5. components.json

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "radix-nova",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

`tailwind.config` stays an empty string for Tailwind v4. Use `"rsc": false` for Vite. Point `tailwind.css` at your real CSS entry file. `style`, `baseColor` and `cssVariables` cannot change after init.

## 6. cn() helper

```bash
bun add shadcn class-variance-authority cn lucide-react tw-animate-css
```

```ts
// src/lib/utils.ts
export { cn } from "cn"
```

Generated components import `cn` from the `cn` package directly. Existing projects on `clsx` plus `tailwind-merge` can move with `bunx --bun shadcn@latest migrate cn`.

## 7. Migrating from Tailwind v3

1. Run `bunx @tailwindcss/upgrade` (Node 20+, clean git tree) and review the diff.
2. Delete `tailwind.config.*`; move colors, fonts and breakpoints into `@theme` / `@theme inline` in CSS (see the `tailwind` skill).
3. Move `:root` / `.dark` variables out of `@layer base`, wrap bare HSL channel values in `hsl()` (or convert to OKLCH), and add `@theme inline` entries that reference them with `var(--name)`.
4. Replace the `tailwindcss-animate` plugin with `@import "tw-animate-css";`.
5. Set `"config": ""` in `components.json`.
6. Optional: remove `forwardRef` (React 19 codemod), swap `w-* h-*` for `size-*`, replace the deprecated `toast` component with `sonner`.
7. Existing components keep working until you re-add them; `bunx --bun shadcn@latest add <name> --diff` shows upstream changes.

## 8. Validation

```bash
# No v3 config files (expect no output)
find . -name "tailwind.config.*" -not -path "*/node_modules/*"

# Entry CSS imports Tailwind, tw-animate-css and defines the dark variant
grep -n '@import "tailwindcss"\|tw-animate-css\|@custom-variant dark' src/app/globals.css

# components.json has an empty tailwind.config
grep -n '"config"' components.json

# Build proves the wiring
bun run build
```

## Troubleshooting

- **CLI created `tailwind.config.js`**: delete it and set `"config": ""`; it came from a v3-era template.
- **Components unstyled**: the CSS entry file is not imported in the root layout, `@import "tailwindcss"` is missing, or the `@theme inline` mapping lacks a token.
- **Dark mode does nothing**: `@custom-variant dark (&:is(.dark *));` is missing, the `.dark` class is not toggled on `<html>`, or `@theme` was used where `@theme inline` is needed.
- **`Cannot find module '@/lib/utils'` or `'cn'`**: alias missing in tsconfig or Vite (step 3), or `bun add cn` was skipped.
- **Type errors on `React`**: `bun add -D @types/react @types/react-dom`.
- **Colors differ from the docs after init**: the preset or base color changed; run `bunx --bun shadcn@latest preset resolve` to see what the project uses.
