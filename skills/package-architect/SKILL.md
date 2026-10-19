---
name: package-architect
description: Designs TypeScript monorepo packages — package.json exports, tsconfig references, build config. Use when creating or restructuring workspace packages.
metadata:
  version: "2.2.4"
  tags: "packages, monorepo, typescript"
when_to_use: "workspace package, exports map, tsconfig references"
---

# Package Architect

Design reusable TypeScript packages in monorepos (Bun workspaces preferred; pnpm and npm workspaces also work).

## When to use

- Creating new packages or restructuring monorepo packages
- Defining `package.json` exports
- Setting up tsconfig references

## Core principles

- Single responsibility per package.
- Stable public APIs with clear exports.
- Avoid inline interfaces; centralize types.
- Keep build outputs separated from sources.

## Package structure (example)

```
packages/
  utils/
    src/
    package.json
    tsconfig.json
  api-client/
    src/
    package.json
    tsconfig.json
```

## Exports pattern (example)

Put the `types` condition first; conditions are matched in order, so a later `types` can be ignored.

```json
{
  "name": "@scope/utils",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  }
}
```

## TypeScript references

- Use project references for inter-package dependencies.
- Prefer path aliases for local dev imports.
- Keep the tsconfig base shared across packages.

## Checklist

- Exports map matches the intended public API
- Types build alongside JS output
- No circular dependencies
- Consistent lint and tsconfig settings
