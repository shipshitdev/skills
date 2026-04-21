---
name: de-slop
description: Remove AI-generated code artifacts (console.log, any types, unused imports, dead code) while maintaining project structure. Use when user says 'de-slop', 'clean up', 'remove slop', or 'clean AI artifacts'.
metadata:
  version: 1.0.0
  tags: code-quality, cleanup, ai-artifacts, maintenance
---

# De-Slop

Remove AI-generated artifacts and code sloppiness while maintaining project structure.

## What Gets Cleaned

1. **Console statements** — Replace with logger service
2. **`any` types** — Replace with proper types/interfaces
3. **Unused imports** — Remove completely
4. **Commented-out code** — Remove dead code blocks
5. **Temporary/debug code** — Remove TODO/FIXME debug statements
6. **Obvious AI comments** — Remove redundant comments
7. **Unused variables** — Remove if truly unused

## Workflow

### Step 1: Check Critical Rules

Read project rules before making changes:

```bash
cat .agents/SYSTEM/critical/CRITICAL-NEVER-DO.md 2>/dev/null || true
```

### Step 2: Detect Project Structure

Determine if monorepo or single project:

```bash
ls packages/ 2>/dev/null || ls pnpm-workspace.yaml 2>/dev/null || true
```

If monorepo: process each package separately.

### Step 3: Identify Artifacts

Search for each artifact type across the codebase.

### Step 4: Execute Cleanup (Per Package)

For each package/project:

1. Console statements — Replace with logger
2. `any` types — Create interfaces, replace types
3. Unused imports — Remove
4. Commented code — Remove blocks
5. Debug code — Remove temporary code
6. Obvious comments — Remove redundant comments
7. Unused variables — Remove

### Step 5: Verify

```bash
npm run type-check || tsc --noEmit
npm test
```

### Step 6: Document

Log cleanup in session file with packages cleaned and artifact counts.

## Options

- Default: clean current package/project
- `--all`: clean across entire monorepo
- `--check`: dry run, show what would be cleaned

## Safety Rules

- Never delete critical files (README, configs, entry points)
- Respect logger service patterns
- Be careful with side-effect imports (CSS, polyfills)
- Keep comments that explain "why", remove comments that restate "what"
