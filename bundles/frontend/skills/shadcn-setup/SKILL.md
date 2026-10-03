---
name: shadcn-setup
description: >-
  Sets up shadcn/ui with Tailwind CSS v4 CSS-first configuration — installs
  packages, generates globals.css with @theme tokens, creates components.json,
  and adds the cn() utility. Use when starting a new Next.js or React project
  that needs a shadcn component library, or migrating from shadcn + Tailwind v3.
metadata:
  version: "2.2.2"
  tags: "shadcn, ui, components, tailwind, react, nextjs"
---

# shadcn/ui Setup

Sets up shadcn/ui with the modern CSS-first Tailwind v4 setup, not the deprecated v3 approach.

## Authorized Scope

Apply this engine only within the user's requested task and existing explicit
authorization. Loading or delegating to it grants no additional authority.
Preserve report-only restrictions and the caller's target, host, provider, and
cost limits. Existing approval satisfies a gate only for the same actions and
scope; obtain approval before expanding them. Forward these limits to delegates.

## Contract

Inputs:

- Project root directory (defaults to current working directory).
- Optional: theme name (zinc, slate, stone, etc.), component list, router type (app-router or pages-router).

Outputs:

- `globals.css` with `@import "tailwindcss"` and full `@theme` token block.
- `components.json` with CSS-first shadcn config.
- `src/lib/utils.ts` with `cn()` helper.
- Installed packages: `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`, `tailwindcss`, `@tailwindcss/postcss`.

Creates/Modifies:

- `src/app/globals.css` (created or overwritten).
- `components.json` (created or overwritten).
- `src/lib/utils.ts` (created).
- `package.json` (dependencies updated via `bun add`).
- `postcss.config.mjs` (created if absent).

External Side Effects:

- Runs `bun add` to install packages.
- Runs `bunx shadcn@latest add` for any specified components.

Confirmation Required:

- Apply only the explicitly requested setup or migration. Invocation alone
  grants no permission to replace existing styles or configuration.
- Confirm before overwriting files or installing components beyond that scope.

Delegates To:

- `bunx shadcn@latest add` for individual component installation.

## Purpose

**IMPORTANT**: shadcn/ui CLI and AI assistants often generate Tailwind v3 configs by default. This skill ensures:

- Tailwind v4 CSS-first configuration
- Proper `@theme` block with shadcn color tokens
- No deprecated `tailwind.config.js` files
- Correct dependency versions

## When to Use

- Setting up a new Next.js project with shadcn/ui
- Adding shadcn/ui to an existing project
- Migrating from shadcn + Tailwind v3 to v4
- Resetting a broken shadcn configuration

## Quick Start

```bash
# Install core dependencies
bun add class-variance-authority clsx tailwind-merge lucide-react
bun add -D tailwindcss @tailwindcss/postcss

# Initialize shadcn (CSS-first, no tailwind.config)
bunx shadcn@latest init

# Install specific components
bunx shadcn@latest add button card input dialog

# Or install an essential starter set
bunx shadcn@latest add button card input label dialog dropdown-menu toast
```

## What Gets Installed

### Dependencies

See `references/examples.md` (§ Dependency Versions Example) for the full dependency block.

### File Structure

See `references/examples.md` (§ Generated File Structure) for the full tree.

## Tailwind v4 + shadcn CSS Configuration

The skill generates a CSS-first configuration using `@import "tailwindcss"` and an `@theme` block with all shadcn color tokens and border-radius variables.

See `${CLAUDE_SKILL_DIR}/references/shadcn-theme-tokens.md` for the full token block (load when constructing the globals.css file).

## Available Themes

| Theme | Description |
|-------|-------------|
| `default` | shadcn default (neutral grays) |
| `zinc` | Zinc-based neutral |
| `slate` | Slate-based cool neutral |
| `stone` | Stone-based warm neutral |
| `gray` | Pure gray |
| `neutral` | True neutral |
| `red` | Red primary |
| `rose` | Rose primary |
| `orange` | Orange primary |
| `green` | Green primary |
| `blue` | Blue primary |
| `yellow` | Yellow primary |
| `violet` | Violet primary |

## Common Components

Install commonly used components:

```bash
# Essential set
bunx shadcn@latest add button card input label dialog dropdown-menu toast

# Form-focused
bunx shadcn@latest add form input label select checkbox radio-group switch textarea

# Dashboard
bunx shadcn@latest add card table tabs badge avatar dropdown-menu sheet sidebar
```

## components.json Configuration

See `references/examples.md` (§ components.json Full Example) for the full config. The `tailwind.config` field stays empty because setup uses CSS-first configuration in v4.

## Utils File

```typescript
// src/lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Usage After Setup

### Adding Components

```bash
# Using bunx (recommended with bun)
bunx shadcn@latest add button

# Multiple components
bunx shadcn@latest add card dialog dropdown-menu
```

### Using Components

See `references/examples.md` (§ Using Components Example) for a sample composition.

## Dark Mode Support

The CSS uses `prefers-color-scheme` by default. For manual toggle, see `references/examples.md` (§ Dark Mode — Manual Toggle Provider) for the provider component and class-based CSS override.

## Troubleshooting

### "tailwind.config.js created by shadcn CLI"

Delete it. The CLI sometimes generates v3 configs. Run:

```bash
rm tailwind.config.js tailwind.config.ts
```

### Components not styled correctly

1. Check that `globals.css` is imported in your layout
2. Verify `@import "tailwindcss"` is at the top
3. Ensure `@theme` block contains all required variables

### Type errors with components

Run:

```bash
bun add -D @types/react @types/react-dom
```

### cn() utility not found

Create `src/lib/utils.ts`:

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## Validation

After setup, verify no v3 patterns were introduced:

```bash
# Should return nothing (no v3 tailwind.config files)
find . -name "tailwind.config.*" -not -path "*/node_modules/*"

# Should return nothing (no @apply directives)
grep -r "@apply" src/ --include="*.css" 2>/dev/null

# Verify the @import directive is present
grep "@import \"tailwindcss\"" src/app/globals.css
```
