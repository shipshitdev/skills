---
name: linter-formatter-init
description: Sets up Biome (default) or ESLint + Prettier, Vitest, and pre-commit hooks for JavaScript/TypeScript projects with Bun. Use when initializing quality tooling or adding linting.
metadata:
  version: "2.2.2"
  tags: "linting, formatting, setup"
when_to_use: "lint setup, formatter config"
---

# Linter Formatter Init

Set up linting, formatting, and testing for JavaScript/TypeScript projects using **Biome 2.3+** (default), **Vitest**, and **Bun**.

**IMPORTANT**: Always uses Biome 2.3+ (latest) - never older versions.

## Contract

Inputs:

- Target repository and selected formatter, testing, and hook options

Outputs:

- Configured quality tooling and a summary of changes

Creates/Modifies:

- Only the configuration, scripts, and dependencies selected for setup

External Side Effects:

- Package installs and permitted local verification

Confirmation Required:

- Before overwriting existing configuration or installing tools outside the explicitly requested setup
- Loading the skill grants no additional authority. Existing explicit approval
  applies only to the same target and actions; preserve report-only restrictions.

Delegates To:

- None

## Purpose

This skill automates the setup of:

- **Biome** for linting + formatting (default, recommended)
- **Vitest** for testing with coverage (use `--vitest` flag)
- ESLint + Prettier (legacy, use `--eslint` flag)
- Husky + lint-staged for pre-commit hooks
- VS Code/Cursor settings for auto-format on save
- bun scripts for manual linting, formatting, and testing

## When to Use

- Starting a new JS/TS project
- Adding linting to an existing project without tooling
- Standardizing code quality across a team
- Setting up pre-commit hooks to enforce quality

## Quick Start

```bash
# Default setup (Biome) - RECOMMENDED
python3 scripts/setup.py --root /path/to/project

# Add Vitest testing with 80% coverage threshold
python3 scripts/setup.py --root /path/to/project --vitest --coverage 80

# Use ESLint + Prettier instead (legacy)
python3 scripts/setup.py --root /path/to/project --eslint --typescript
```

See `references/full-guide.md` (§ Quick Start — Full Command Variants) for `--no-hooks`, `--monorepo`, and every flag combination.

## What Gets Installed

### Dependencies

**Biome 2.3+ (default):** `@biomejs/biome@latest` (always latest, minimum 2.3+)

**Vitest (with `--vitest`):** `vitest`, `@vitest/coverage-v8`

**ESLint + Prettier (legacy, with `--eslint`):** `eslint`, `prettier`, `eslint-config-prettier`, `eslint-plugin-prettier`, plus `@typescript-eslint/parser` and `@typescript-eslint/eslint-plugin` if `--typescript`

**Pre-commit hooks:** `husky`, `lint-staged`

### Configuration Files (Biome - Default)

```
project/
├── biome.json              # Biome config (lint + format)
├── .vscode/settings.json   # Auto-format on save
├── .husky/pre-commit       # Pre-commit hook
└── package.json            # Updated with scripts + lint-staged
```

ESLint + Prettier (legacy) produces the equivalent `.eslintrc.json` / `.prettierrc` layout — see `references/full-guide.md` (§ Configuration Files (ESLint + Prettier - Legacy)).

### Bun Scripts Added

Biome adds `lint`, `lint:fix`, `format`, `format:check`, `check`, `check:fix`. Vitest adds `test`, `test:watch`, `test:coverage`, `test:ui`. ESLint + Prettier (legacy) adds `lint`, `lint:fix`, `format`, `format:check`. See `references/full-guide.md` (§ Bun Scripts Added) for the exact script commands.

## Biome Configuration (Default)

Biome is a fast, all-in-one linter and formatter. The default config enables recommended lint rules, 2-space/100-char formatting, single quotes, and `organizeImports`. See `references/full-guide.md` (§ Biome Configuration (Default)) for the full `biome.json`.

After setup, customize `biome.json` to adjust linting rules, formatting preferences, and file ignore patterns.

## Vitest Configuration (with --vitest)

The `--vitest` flag creates `vitest.config.ts` (node/jsdom environment, v8 coverage, 80% default thresholds) and `src/test/setup.ts` for global test setup. See `references/full-guide.md` (§ Vitest Configuration (with --vitest)) for both files in full.

Customize the coverage threshold with `--coverage 90`.

## Pre-commit Hooks

When enabled (default), lint-staged runs on every commit:

**Biome:** `*.{js,jsx,ts,tsx,json,css}` → `bunx biome check --write`

**ESLint + Prettier (legacy):** `*.{js,jsx,ts,tsx}` → `eslint --fix`, `prettier --write`; `*.{json,md,yml,yaml}` → `prettier --write`

This ensures all committed code passes linting, is formatted, and no broken code enters the repo.

## VS Code / Cursor Integration

The skill creates `.vscode/settings.json` enabling format-on-save with Biome (default) or Prettier/ESLint (legacy) as the default formatter. See `references/full-guide.md` (§ VS Code / Cursor Settings) for both full configs.

## Why Biome Over ESLint + Prettier?

- **Faster**: Written in Rust, 10-100x faster than ESLint + Prettier
- **Simpler**: One tool instead of two, one config file
- **No conflicts**: No need for eslint-config-prettier or similar workarounds
- **Better defaults**: Sensible rules out of the box

## Monorepo Support

Run `python3 scripts/setup.py --root /path/to/monorepo --monorepo` from the root. This adds root-level config that applies to all packages.

## Troubleshooting

### Pre-commit hooks not running

```bash
bunx husky
chmod +x .husky/pre-commit
```

### Format on save not working (Biome)

1. Install the Biome extension in VS Code/Cursor
2. Set Biome as default formatter
3. Enable "Format on Save" in settings

### Format on save not working (ESLint + Prettier)

1. Install the Prettier extension in VS Code/Cursor
2. Set Prettier as default formatter
3. Enable "Format on Save" in settings

## Framework-Specific Configs (ESLint mode only)

When using `--eslint`, the skill detects common frameworks and adjusts config:

- **Next.js**: Adds `next/core-web-vitals` to ESLint
- **React**: Adds `eslint-plugin-react` and `eslint-plugin-react-hooks`
- **NestJS**: Adds rules for decorators and DI patterns

## Manual Setup (Alternative)

If preferring manual setup over the script:

```bash
# Biome
bun add -D @biomejs/biome husky lint-staged
bunx biome init && bunx husky
```

See `references/full-guide.md` (§ Manual Setup (Alternative to the setup script)) for the ESLint + Prettier manual sequence, then copy configs from `assets/configs/`.
