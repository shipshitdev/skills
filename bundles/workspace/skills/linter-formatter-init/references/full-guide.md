# Linter Formatter Init — Full Guide

Full command variants and config dumps for the linter-formatter-init skill. See `SKILL.md` for purpose, when-to-use triggers, and the short defaults.

## Quick Start — Full Command Variants

```bash
# Default setup (Biome) - RECOMMENDED
python3 scripts/setup.py \
  --root /path/to/project

# Use ESLint + Prettier instead (legacy)
python3 scripts/setup.py \
  --root /path/to/project \
  --eslint

# ESLint + Prettier with TypeScript
python3 scripts/setup.py \
  --root /path/to/project \
  --eslint \
  --typescript

# Skip pre-commit hooks
python3 scripts/setup.py \
  --root /path/to/project \
  --no-hooks

# Add Vitest testing with 80% coverage threshold
python3 scripts/setup.py \
  --root /path/to/project \
  --vitest

# Full setup: Biome + Vitest + Husky
python3 scripts/setup.py \
  --root /path/to/project \
  --vitest \
  --coverage 80

# Monorepo (root-level config applied to all packages)
python3 scripts/setup.py \
  --root /path/to/monorepo \
  --monorepo
```

## Configuration Files (ESLint + Prettier - Legacy)

```
project/
├── .eslintrc.json          # ESLint config
├── .prettierrc             # Prettier config
├── .prettierignore         # Prettier ignore patterns
├── .eslintignore            # ESLint ignore patterns
├── .vscode/
│   └── settings.json       # Auto-format on save
├── .husky/
│   └── pre-commit          # Pre-commit hook
└── package.json            # Updated with scripts + lint-staged
```

## Bun Scripts Added

**Biome:**

```json
{
  "scripts": {
    "lint": "biome lint .",
    "lint:fix": "biome lint --write .",
    "format": "biome format --write .",
    "format:check": "biome format .",
    "check": "biome check .",
    "check:fix": "biome check --write ."
  }
}
```

**Vitest:**

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

**ESLint + Prettier (legacy):**

```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

## Biome Configuration (Default)

```json
{
  "$schema": "https://biomejs.dev/schemas/2.5.15/schema.json",
  "assist": {
    "actions": {
      "source": { "organizeImports": "on" }
    }
  },
  "linter": {
    "enabled": true,
    "rules": {
      "preset": "recommended",
      "complexity": { "noForEach": "off" },
      "style": { "noNonNullAssertion": "off" },
      "suspicious": { "noArrayIndexKey": "off", "noExplicitAny": "warn" }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "es5",
      "semicolons": "always"
    }
  },
  "files": {
    "includes": [
      "**",
      "!**/node_modules",
      "!**/dist",
      "!**/build",
      "!**/.next",
      "!**/out",
      "!**/.cache",
      "!**/.turbo",
      "!**/coverage",
      "!**/*.min.js",
      "!**/*.min.css"
    ]
  }
}
```

Biome 2 replaced the old `files.ignore` list with `files.includes` plus `!` exclusions.

## Vitest Configuration (with --vitest)

`vitest.config.ts`:

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node", // or "jsdom" for frontend
    include: ["src/**/*.{test,spec}.{ts,tsx}", "**/*.{test,spec}.{ts,tsx}"],
    exclude: ["node_modules", "dist", ".next", "build"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      include: ["src/**/*.ts", "src/**/*.tsx"],
      exclude: ["src/**/*.test.ts", "src/**/*.spec.ts", "src/**/*.d.ts"],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
    mockReset: true,
    restoreMocks: true,
  },
});
```

`src/test/setup.ts` for global test configuration:

```typescript
import { expect, afterEach } from "vitest";
import { cleanup } from "@testing-library/react"; // For React projects

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

## VS Code / Cursor Settings

**Biome (default):**

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "editor.codeActionsOnSave": {
    "source.organizeImports.biome": "explicit",
    "quickfix.biome": "explicit"
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  }
}
```

**ESLint + Prettier (legacy):**

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  }
}
```

## Manual Setup (Alternative to the setup script)

**Biome:**

```bash
bun add -D @biomejs/biome husky lint-staged
bunx biome init
bunx husky
```

**ESLint + Prettier:**

```bash
bun add -D eslint prettier eslint-config-prettier eslint-plugin-prettier husky lint-staged
bun add -D @typescript-eslint/parser @typescript-eslint/eslint-plugin
bunx eslint --init
bunx husky
```

Then copy configs from `assets/configs/`.
