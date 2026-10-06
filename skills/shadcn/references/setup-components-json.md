---
title: Configure components.json Before Adding Components
impact: CRITICAL
impactDescription: prevents path resolution failures across all component imports
tags: setup, components-json, configuration, cli, paths, tailwind-v4
---

## Configure components.json Before Adding Components

The components.json file tells the CLI where to place components and how to resolve imports. Missing or incorrect configuration causes every component addition to fail or generate incorrect import paths. With Tailwind CSS v4 there is no `tailwind.config.*` file, so `tailwind.config` must be an empty string.

**Incorrect (v3-style config path and missing aliases):**

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/styles/globals.css"
  }
}
// CLI looks for a config file that does not exist in a v4 project
// and generates imports like: import { Button } from "components/ui/button"
```

**Correct (Tailwind v4: empty config, CSS entry file, aliases):**

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "radix-nova",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/styles/globals.css",
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

**Notes:**

- `tailwind.css` points at the file that starts with `@import "tailwindcss";`. The CLI writes tokens and `@theme inline` there.
- `style` is `<base>-<preset>` (for example `radix-nova`) and `baseColor` and `cssVariables` cannot be changed after initialization.
- Generate the file instead of writing it by hand: `bunx --bun shadcn@latest init`. Pass `--base radix --preset nova` for a non-interactive Radix setup.

Reference: [shadcn/ui components.json](https://ui.shadcn.com/docs/components-json)
