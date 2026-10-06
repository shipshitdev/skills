---
name: stack-validator
description: Validates Biome 2.3+, Bun workspace, Next.js 16 and Tailwind v4 config and flags deprecated patterns. Use before stack work or when AI-generated config may be outdated.
metadata:
  version: "2.2.2"
  tags: "biome, bun, nextjs, tailwind, validation, configuration, code-quality"
when_to_use: "biome.json check, middleware.ts to proxy.ts, @theme v3 leftovers, bun workspace"
---

# Stack Validator

One validator for the Shipshit.dev stack. Each stack keeps its own checks, behind one
script, one report format, and one set of flags. Run it before stack work, after AI
generates config, and in CI.

## When This Activates

- Setting up or auditing a Biome, Bun, Next.js, or Tailwind project
- Before any code-quality, routing, or styling work on that stack
- After AI generates `biome.json`, `package.json`, `next.config.*`, or Tailwind CSS
- CI/CD pipeline validation

## Quick Start

```bash
python3 scripts/validate.py --root .                      # auto-detect stacks from the project
python3 scripts/validate.py --root . --stack nextjs       # one stack
python3 scripts/validate.py --root . --stack biome --stack tailwind --strict
python3 scripts/validate.py --root . --stack all --json
```

Auto-detection picks a stack from `package.json` dependencies or its config files:
`@biomejs/biome` or `biome.json`; `bun.lock`, legacy `bun.lockb` or `bunfig.toml`; `next`; `tailwindcss`. With none detected the script exits with an error and
asks for `--stack`. Run from the skill directory, or use the installed path to
`scripts/validate.py`.

## Stacks

| Stack | Validates | Flags | Reference |
|---|---|---|---|
| `biome` | `@biomejs/biome` 2.3+, `$schema` version, linter rules and domains, `assist.actions` | `organizeImports` at root, missing domains, leftover ESLint/Prettier configs | `references/biome.md` |
| `bun` | Bun 1.3+, private root, workspaces, catalogs, `workspace:` protocol, one root `bun.lock` (a lone legacy `bun.lockb` warns, both is an error) | dependencies in root, lockfiles inside workspaces, hardcoded local versions | `references/bun.md` |
| `nextjs` | `next` 16+, App Router, `proxy.ts`, `use cache`, `next.config.ts` | `middleware.ts`, `pages/` pages, `getServerSideProps`/`getStaticProps`, `next/router` | `references/nextjs.md` |
| `tailwind` | `tailwindcss` 4+, `@import "tailwindcss"`, `@theme`, `@tailwindcss/postcss` | `tailwind.config.*`, `@tailwind` directives, `autoprefixer`, old PostCSS plugin | `references/tailwind.md` |

Read the reference for the stack being validated: it holds the GOOD/BAD examples,
deprecated-pattern tables, migration steps, and full guide. Open only that file.

## Flags

| Flag | Effect |
|---|---|
| `--root <dir>` | Project root (default `.`) |
| `--stack <name>` | Stack to validate; repeat for several, or `all`. Default: auto-detect |
| `--strict` | Treat warnings as errors (exit 1 on any warning or error) |
| `--ci` | Exit 1 on errors |
| `--verbose` | List passed checks |
| `--json` | One stack: that stack's report object. Several: an object keyed by stack |

Without `--ci` or `--strict` the script reports and exits 0.

## CI/CD Integration

```yaml
# .github/workflows/validate.yml
- name: Validate stack config
  run: |
    python3 scripts/validate.py \
      --root . \
      --stack all \
      --strict \
      --ci
```

Pass only the stacks the project uses; `--stack all` validates every stack and reports
a missing dependency as an error.

## Integration

- `linter-formatter-init` - Sets up Biome from scratch
- `project-init-orchestrator` - Creates workspace structure
- `git-safety` - Ensures no secrets are committed
