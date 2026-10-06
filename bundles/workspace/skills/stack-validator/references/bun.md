# Bun 1.3+ workspaces validator reference

Checks, deprecated patterns, and examples for the `bun` stack of `scripts/validate.py --stack bun`.

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

**GOOD:** See the Full guide section below (§ Workspace Structure Example) for the full tree — root `package.json` + `bun.lock`, each app/package owns its own `package.json`.

**BAD:**

```
my-monorepo/
├── package.json
├── apps/
│   └── web/
│       ├── package.json
│       └── bun.lock      # BAD: Lockfile in workspace
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

`bun.lock` (the text lockfile, default since Bun 1.2) is the canonical lockfile: keep exactly one at the root and none inside workspaces. A lone legacy binary `bun.lockb` is still accepted but reported as a warning with a migration command; `bun.lock` and `bun.lockb` together is an error.

```bash
# Migrate a legacy binary lockfile
bun install --save-text-lockfile --frozen-lockfile --lockfile-only
rm bun.lockb
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
rm apps/*/bun.lock packages/*/bun.lock
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

See the Full guide section below (§ Validation Output Example) for a sample report.

## Best Practices

- Always use the workspace protocol: `"@myorg/shared": "workspace:*"`
- Use `--cwd` for workspace operations: `bun add lodash --cwd apps/web` (not `cd apps/web && bun add`)
- Run `bun install` only from the root — keep a single lockfile
- Use dependency catalogs for shared versions (see § Dependency Catalogs above)
- Declare all dependencies explicitly per workspace — don't rely on hoisting

## Full guide

### Workspace Structure Example (GOOD)

```
my-monorepo/
├── package.json          # Root with workspaces, private: true
├── bun.lock              # Single lockfile at root
├── apps/
│   ├── web/
│   │   └── package.json  # Own dependencies
│   └── api/
│       └── package.json  # Own dependencies
└── packages/
    ├── ui/
    │   └── package.json  # Shared package
    └── config/
        └── package.json  # Shared config
```

### Validation Output Example

```
=== Bun Workspace Validation Report ===

Bun Version: 1.3.2 ✓

Root package.json:
  ✓ private: true
  ✓ workspaces defined
  ✗ Found dependencies in root (should be empty)

Workspace Structure:
  ✓ apps/web - valid workspace
  ✓ apps/api - valid workspace
  ✓ packages/ui - valid workspace
  ✗ apps/web/bun.lock - lockfile should only be at root

Dependencies:
  ✓ Using workspace:* protocol
  ✗ @myorg/ui uses hardcoded version "1.0.0"

Catalogs:
  ✗ No dependency catalog found (recommended for Bun 1.3+)

Summary: 3 issues found
```
