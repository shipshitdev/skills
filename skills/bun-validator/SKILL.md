---
name: bun-validator
description: "Validates Bun workspace config and monorepo setup: catalogs, isolated installs, Bun 1.3+ practices. Use when setting up or auditing a Bun monorepo or adding workspace dependencies."
metadata:
  version: "2.2.2"
  tags: "bun, monorepo, workspace, validation, package-manager"
when_to_use: "package.json in CI"
---

# Bun Validator

## When This Activates

- Setting up a new Bun monorepo
- Before adding dependencies to workspaces
- Auditing existing Bun workspaces
- After AI generates package.json files
- CI/CD pipeline validation

## Quick Start

```bash
python3 scripts/validate.py --root .
python3 scripts/validate.py --root . --strict
```

## What Gets Checked

### 1. Bun Version

```bash
# GOOD: v1.3+
bun --version  # 1.3.0 or higher

# BAD: v1.2 or earlier
bun --version  # 1.2.x
```

### 2. Root package.json

**GOOD - Monorepo root:**

```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"]
}
```

**BAD - Dependencies in root:**

```json
{
  "workspaces": ["apps/*"],
  "dependencies": {
    "react": "^19.0.0"  // BAD: Don't put deps in root
  }
}
```

### 3. Workspace Structure

**GOOD:** See `references/full-guide.md` (§ Workspace Structure Example) for the full tree — root `package.json` + `bun.lockb`, each app/package owns its own `package.json`.

**BAD:**

```
my-monorepo/
├── package.json
├── apps/
│   └── web/
│       ├── package.json
│       └── bun.lockb     # BAD: Lockfile in workspace
```

### 4. Workspace Dependencies

**GOOD - Using workspace protocol:**

```json
{
  "dependencies": {
    "@myorg/ui": "workspace:*",
    "@myorg/config": "workspace:^1.0.0"
  }
}
```

**BAD - Hardcoded versions:**

```json
{
  "dependencies": {
    "@myorg/ui": "1.0.0"  // BAD: Use workspace:*
  }
}
```

### 5. Dependency Catalogs (Bun 1.3+)

**GOOD - Centralized versions:**

```json
// Root package.json
{
  "catalog": {
    "react": "^19.0.0",
    "typescript": "^5.7.0",
    "@types/node": "^22.0.0"
  }
}
```

```json
// apps/web/package.json
{
  "dependencies": {
    "react": "catalog:"  // Uses version from catalog
  }
}
```

### 6. Isolated Installs

**GOOD - Default in Bun 1.3:**
Packages can only access dependencies they explicitly declare.

**BAD - Hoisted dependencies:**

```json
// Don't disable isolation
{
  "workspaces": {
    "packages": ["apps/*"],
    "nohoist": ["**"]  // Don't do this
  }
}
```

## Bun 1.3+ Features

### Dependency Catalogs

See § Dependency Catalogs (Bun 1.3+) above for the catalog syntax.

### Interactive Updates

```bash
bun update --interactive  # Selectively update deps
```

### Dependency Chains

```bash
bun why react  # Explain why a package is installed
```

### Workspace Commands

```bash
# Install in specific workspace
bun add express --cwd apps/api

# Run script in workspace
bun run --cwd apps/web dev

# Run in all workspaces
bun run --filter '*' build
```

## Common Issues

### Issue: "Cannot find module"

**Cause:** Dependency not declared in workspace package.json

**Fix:**

```bash
bun add <package> --cwd <workspace>
```

### Issue: Multiple lockfiles

**Cause:** Running `bun install` in workspace directory

**Fix:**

```bash
rm apps/*/bun.lockb packages/*/bun.lockb
bun install  # From root only
```

### Issue: Version conflicts

**Cause:** Same package with different versions across workspaces

**Fix:** Use dependency catalogs:

```json
{
  "catalog": {
    "problematic-package": "^1.0.0"
  }
}
```

## Validation Output

See `references/full-guide.md` (§ Validation Output Example) for a sample report.

## Best Practices

- Always use the workspace protocol: `"@myorg/shared": "workspace:*"`
- Use `--cwd` for workspace operations: `bun add lodash --cwd apps/web` (not `cd apps/web && bun add`)
- Run `bun install` only from the root — keep a single lockfile
- Use dependency catalogs for shared versions (see § Dependency Catalogs above)
- Declare all dependencies explicitly per workspace — don't rely on hoisting

## CI/CD Integration

```yaml
# .github/workflows/validate.yml
- name: Validate Bun Workspace
  run: |
    python3 scripts/validate.py \
      --root . \
      --strict \
      --ci
```

## Integration

- `linter-formatter-init` - Sets up Biome with Bun
- `project-init-orchestrator` - Creates workspace structure
- `nextjs-validator` - Validates Next.js in workspace
