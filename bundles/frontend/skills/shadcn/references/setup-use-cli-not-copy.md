---
title: Use CLI to Add Components Instead of Copy-Paste
impact: CRITICAL
impactDescription: ensures correct imports, dependencies, and file structure
tags: setup, cli, bunx, shadcn, add, installation
---

## Use CLI to Add Components Instead of Copy-Paste

The CLI handles import paths, peer dependencies, and file placement automatically. Manual copying often misses dependencies or uses wrong import paths.

**Incorrect (manual copy without dependencies):**

```typescript
// Copied button.tsx manually
import { Slot } from "radix-ui"
// Error: radix-ui is not installed

import { cva, type VariantProps } from "class-variance-authority"
// Error: class-variance-authority is not installed
```

**Correct (CLI installation):**

```bash
# Installs the component with all dependencies
bunx --bun shadcn@latest add button

# Adds: radix-ui, class-variance-authority (as needed)
# Creates: components/ui/button.tsx with correct imports
```

**Adding multiple components:**

```bash
# Add multiple components at once
bunx --bun shadcn@latest add button card dialog input

# Add all components
bunx --bun shadcn@latest add --all
```

**Useful CLI commands:**

```bash
bunx --bun shadcn@latest add button --dry-run   # preview files without writing
bunx --bun shadcn@latest add button --diff      # compare against your local copy
bunx --bun shadcn@latest view button            # read the registry source first
bunx --bun shadcn@latest search @shadcn -q "sidebar"
```

Without `--overwrite` the CLI asks before replacing a component you may have edited.

Reference: [shadcn/ui CLI](https://ui.shadcn.com/docs/cli)
