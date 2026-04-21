---
name: turborepo
description: |
  Turborepo monorepo build system guidance. Triggers on: turbo.json, task pipelines,
  dependsOn, caching, remote cache, the "turbo" CLI, --filter, --affected, CI optimization, environment
  variables, internal packages, monorepo structure/best practices, and boundaries.

  Use when user: configures tasks/workflows/pipelines, creates packages, sets up
  monorepo, shares code between apps, runs changed/affected packages, debugs cache,
  or has apps/packages directories.
metadata:
  version: 2.9.7-canary.12
---

# Turborepo Skill

Build system guidance for JavaScript and TypeScript monorepos using Turborepo.

## Core Rules

1. Create package tasks, not root tasks.
2. Register task behavior in `turbo.json`.
3. Let root `package.json` delegate with `turbo run <task>`.
4. Use `turbo <task>` only for interactive one-off terminal commands, not in committed code.
5. Declare workspace dependencies in `package.json` so `dependsOn: ["^build"]` can resolve actual package relationships.

## Baseline Pattern

```json
// apps/web/package.json
{
  "scripts": {
    "build": "next build",
    "lint": "eslint .",
    "test": "vitest"
  }
}
```

```json
// turbo.json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

```json
// root package.json
{
  "scripts": {
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  }
}
```

## Quick Routing

Read only the reference files needed for the task:

| Need | Read |
| --- | --- |
| Task definitions, `dependsOn`, `outputs`, `persistent`, package overrides | `references/configuration/RULE.md`, `references/configuration/tasks.md` |
| Global options, daemon, cacheDir, env mode | `references/configuration/global-options.md` |
| Cache misses or remote cache | `references/caching/RULE.md`, `references/caching/gotchas.md`, `references/caching/remote-cache.md` |
| Env vars, `.env`, strict vs loose mode | `references/environment/RULE.md`, `references/environment/modes.md`, `references/environment/gotchas.md` |
| `--affected`, `--filter`, package selection | `references/filtering/RULE.md`, `references/filtering/patterns.md` |
| CI, GitHub Actions, Vercel, `turbo-ignore` | `references/ci/RULE.md`, `references/ci/github-actions.md`, `references/ci/vercel.md`, `references/ci/patterns.md`, `references/cli/commands.md` |
| Repo structure, package creation, dependency management | `references/best-practices/RULE.md`, `references/best-practices/structure.md`, `references/best-practices/packages.md`, `references/best-practices/dependencies.md` |
| Watch mode and long-running dev tasks | `references/watch/RULE.md`, `references/configuration/tasks.md` |
| Package boundaries and isolation | `references/boundaries/RULE.md` |

## Decision Trees

### Configure a Task

```
Configure a task?
├─ Define dependencies or outputs → configuration/tasks.md
├─ Handle environment variables → environment/RULE.md
├─ Set package-specific overrides → configuration/RULE.md#package-configurations
├─ Add persistent/watch behavior → configuration/tasks.md + watch/RULE.md
└─ Tune global options → configuration/global-options.md
```

### Debug Caching

```
Cache issue?
├─ Outputs not restored → add or fix `outputs`
├─ Unexpected misses → caching/gotchas.md
├─ Remote cache issue → caching/remote-cache.md
└─ Env or .env drift → environment/gotchas.md
```

### Run Only Changed Work

```
Need changed packages only?
├─ Default path → `turbo run <task> --affected`
├─ Custom comparison base → add `--affected-base=...`
└─ Custom package selection → filtering/RULE.md + filtering/patterns.md
```

### Set Up CI

```
CI setup?
├─ GitHub Actions → ci/github-actions.md
├─ Vercel deployment → ci/vercel.md
├─ Remote cache in CI → caching/remote-cache.md
└─ Skip unchanged work → ci/patterns.md + cli/commands.md
```

### Structure the Monorepo

```
Repo/package structure?
├─ apps/ vs packages/ layout → best-practices/RULE.md
├─ Create internal package → best-practices/packages.md
├─ Workspace dependency management → best-practices/dependencies.md
└─ Enforce package boundaries → boundaries/RULE.md
```

## High-Signal Anti-Patterns

- Root scripts that bypass Turborepo entirely. Root scripts should delegate with `turbo run`, not embed app-specific task logic.
- Committed `turbo build` or `turbo lint` commands in `package.json`, CI, or scripts. Use `turbo run ...` in committed code.
- Manual `prebuild` chains that compile sibling packages instead of declaring workspace dependencies and using `^build`.
- Missing `outputs` on tasks that write files. Read the actual script before deciding whether a task is cacheable.
- Environment variables omitted from `env` or `.env` files omitted from `inputs`, causing stale cache hits.
- Root-level `.env` files in a monorepo, which create hidden coupling between packages.
- Relative imports or file traversal across package boundaries instead of importing through package APIs.
- Package-specific overrides cluttering root `turbo.json` instead of using per-package `turbo.json` files.

See the detailed examples in:

- `references/configuration/gotchas.md`
- `references/caching/gotchas.md`
- `references/environment/gotchas.md`
- `references/best-practices/structure.md`
- `references/best-practices/packages.md`

## Common Configurations

### Standard Build + Dev

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Transit Node for Parallel Tasks With Correct Cache Invalidation

```json
{
  "tasks": {
    "transit": {
      "dependsOn": ["^transit"]
    },
    "lint": {
      "dependsOn": ["transit"]
    }
  }
}
```

Use this when a task can run in parallel but still needs dependency source changes to invalidate its cache.

### Watch Mode Pattern

Use `turbo watch` for file-change loops, not `turbo run ... --watch` patterns improvised in scripts. Read `references/watch/RULE.md` before configuring `persistent`, `interruptible`, or `with`.

## Validation Checklist

- Every committed command in code or CI uses `turbo run ...`.
- Tasks live in package scripts; root scripts only delegate.
- `dependsOn` matches the actual dependency relationship: `^task` for upstream packages, `task` for same-package prerequisites.
- Cacheable file-producing tasks declare `outputs`.
- Relevant environment variables are in `env` or `globalEnv`.
- Relevant `.env` files are represented in `inputs`.
- Workspace packages import each other through package names, not relative source paths.
- CI uses `--affected` or filters when appropriate instead of rebuilding everything by default.

## Source Documentation

Based on official Turborepo docs: `apps/docs/content/docs/` — https://turborepo.dev/docs
