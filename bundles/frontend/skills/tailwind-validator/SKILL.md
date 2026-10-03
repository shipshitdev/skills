---
name: tailwind-validator
description: Validate Tailwind CSS v4 configuration and detect/prevent Tailwind v3 patterns. Use this skill when setting up Tailwind, auditing CSS configuration, or when you suspect outdated Tailwind patterns are being used. Ensures CSS-first configuration with @theme blocks.
metadata:
  version: "2.2.2"
  tags: "tailwind, css, validation, frontend, configuration"
---

# Tailwind 4 Validator

## Purpose

Ensures:

- Projects use Tailwind v4 CSS-first configuration
- Old `tailwind.config.js` patterns are detected and flagged
- Proper `@theme` blocks are used instead of JS config
- Dependencies are v4+

## When to Use

- **Before any Tailwind work**: Run validation first
- **New project setup**: Ensure v4 is installed correctly
- **After AI generates Tailwind code**: Verify no v3 patterns snuck in
- **Auditing existing projects**: Check for migration needs
- **CI/CD pipelines**: Prevent v3 regressions

## Quick Start

```bash
python3 scripts/validate.py --root .
python3 scripts/validate.py --root . --suggest-fixes
python3 scripts/validate.py --root . --strict
```

## What Gets Checked

| Check | Good (v4) | Bad (v3) |
|---|---|---|
| Package version | `"tailwindcss": "^4.0.0"` | `"^3.4.0"` |
| CSS config | `@import "tailwindcss";` + `@theme { --color-primary: ...; }` | `@tailwind base/components/utilities;` |
| Config files | none - config lives in CSS | `tailwind.config.{js,ts,mjs,cjs}` (deprecated in v4) |
| PostCSS | `plugins: { '@tailwindcss/postcss': {} }` only | `tailwindcss` + `autoprefixer` as separate plugins |
| Imports | `@import "tailwindcss/preflight"` / `.../utilities` | `@tailwind` directives |

See `references/full-guide.md` (§ What Gets Checked, § Validation Output) for full GOOD/BAD examples and a sample validation report.

## Migration Guide (v3 to v4)

1. Swap packages: remove `tailwindcss`/`autoprefixer`, add `tailwindcss@latest` + `@tailwindcss/postcss`
2. Point `postcss.config.js` at the `@tailwindcss/postcss` plugin only
3. Convert `tailwind.config.js` theme/extend values into an `@theme { --color-*, --font-*, ... }` block in CSS
4. Replace `@tailwind` directives with `@import "tailwindcss"`
5. Delete `tailwind.config.{js,ts,mjs,cjs}`

See `references/full-guide.md` (§ Migration Guide, § CI/CD Integration) for the exact before/after code per step and a CI workflow snippet.

## Common v3 Patterns to Avoid

| v3 Pattern | v4 Replacement |
|------------|----------------|
| `@tailwind base` | `@import "tailwindcss"` |
| `@tailwind utilities` | `@import "tailwindcss/utilities"` |
| `tailwind.config.js` | `@theme` block in CSS |
| `theme.extend.colors` | `--color-*` CSS variables |
| `theme.extend.spacing` | `--spacing-*` CSS variables |
| `theme.extend.fontFamily` | `--font-*` CSS variables |
| `content: ['./src/**/*.tsx']` | Not needed (auto-detected) |
| `plugins: [require('@tailwindcss/forms')]` | `@plugin "@tailwindcss/forms"` |

See `references/full-guide.md` (§ v4 @theme Reference, § Using with shadcn/ui) for a full `@theme` token example and shadcn/ui token setup.

## Troubleshooting

- **"Found tailwind.config.js but using v4"** - some tools still generate v3 configs. Delete the file and use `@theme` instead.
- **"@tailwind directives found"** - replace with `@import "tailwindcss"`. The old directives are not supported in v4.
- **"autoprefixer in postcss.config"** - remove autoprefixer; it's built into `@tailwindcss/postcss`.
- **"content array in config"** - v4 auto-detects content files. Remove the `content` config entirely.
