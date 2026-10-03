---
name: biome-validator
description: Validate Biome 2.3+ configuration and detect outdated patterns. Ensures proper schema version, domains, assists, and recommended rules. Use before any linting work or when auditing existing projects.
metadata:
  version: "2.2.2"
  tags: "biome, linter, formatter, validation, code-quality"
---

# Biome Validator

## When This Activates

- Setting up linting for a new project
- Before any code quality work
- Auditing existing Biome configurations
- After AI generates biome.json
- CI/CD pipeline validation

## Quick Start

```bash
python3 scripts/validate.py --root .
python3 scripts/validate.py --root . --strict
```

## What Gets Checked

| Check | Good (2.3+) | Bad (legacy) |
|---|---|---|
| Schema version | `"$schema": ".../2.3.12/schema.json"` | `.../1.9.0/schema.json` or older |
| Package version | `"@biomejs/biome": "^2.3.0"` | `"^1.9.0"` or 2.0-2.2 |
| Linter config | `linter.rules.recommended: true` | missing or legacy `rules` shape |
| Assist actions | `assist.actions.source.organizeImports` | top-level `organizeImports.enabled` |
| Domains | `linter.domains.react` / `.next: "on"` | no domains configured |
| Suppression comments | `// biome-ignore lint/<rule>: reason` | `// eslint-disable`, `// @ts-ignore` |

Biome 2.0+ also adds type-aware linting (no TypeScript compiler required) and multi-file lint analysis.

See `references/full-guide.md` (§ What Gets Checked, § Biome 2.3+ Features, § Recommended Configuration) for full GOOD/BAD config examples and a complete recommended `biome.json`.

## Deprecated Patterns

| Deprecated | Replacement (2.3+) |
|------------|-------------------|
| `organizeImports.enabled` | `assist.actions.source.organizeImports` |
| Schema < 2.0 | Schema 2.3.11+ |
| `@biomejs/biome` < 2.3 | `@biomejs/biome@latest` |
| No domains config | Use `linter.domains` for frameworks |

See `references/full-guide.md` (§ Validation Output) for a sample validation report.

## Migration from ESLint

1. Remove ESLint/Prettier packages, add `@biomejs/biome@latest`
2. Generate config: `bunx biome init`
3. Port existing rules: `bunx biome migrate eslint --write`
4. Update `package.json` lint/format scripts to call `biome`
5. Delete old `.eslintrc*` / `.prettierrc*` / `.eslintignore` / `.prettierignore`

See `references/full-guide.md` (§ Migration from ESLint) for the exact commands per step, plus VS Code editor settings and a CI/CD workflow snippet.

## Integration

- `linter-formatter-init` - Sets up Biome from scratch
- `nextjs-validator` - Validates Next.js (enable next domain)
- `bun-validator` - Validates Bun workspace
