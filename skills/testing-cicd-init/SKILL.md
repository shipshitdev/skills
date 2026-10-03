---
name: testing-cicd-init
description: >-
  Installs Vitest testing infrastructure and GitHub Actions CI/CD for TypeScript
  projects (Next.js, NestJS, React). Configures 80% coverage thresholds, test
  setup files, and Bun-based CI workflows. Use when adding tests to a new
  project, migrating from Jest to Vitest, or setting up GitHub Actions CI/CD
  for the first time.
metadata:
  version: "2.2.2"
  tags: "testing, ci, vitest"
---

# Testing & CI/CD Initialization

## Authorized Scope

Apply this engine only within the user's requested task and existing explicit
authorization. Loading or delegating to it grants no additional authority.
Preserve report-only restrictions and the caller's target, host, provider, and
cost limits. Existing approval satisfies a gate only for the same actions and
scope; obtain approval before expanding them. Forward these limits to delegates.

## Contract

Inputs:

- Project root directory (current working directory by default).
- Project type is auto-detected from `package.json` and config files; can be specified explicitly (nextjs, nestjs, react, node).

Outputs:

- `vitest.config.ts` configured for detected environment.
- Test setup file (`src/test/setup.ts` for Next.js/React, `test/setup.ts` for NestJS).
- `.github/workflows/ci.yml` with Bun-based pipeline and coverage enforcement.
- Updated `package.json` scripts (`test`, `test:coverage`, `typecheck`).

Creates/Modifies:

- `vitest.config.ts` (created).
- Test setup file (created).
- `.github/workflows/ci.yml` (created or updated).
- `package.json` scripts section (updated).

External Side Effects:

- Runs `bun add -D` to install Vitest and related testing packages.

Confirmation Required:

- Apply setup only when the user explicitly requested this configuration or
  approved a plan containing it. Invocation alone grants no write authority.
- Confirm before overwriting existing test configuration or adding dependencies
  outside that authorized setup.

Delegates To:

- `husky-test-coverage` skill for adding pre-commit coverage gate (optional, not auto-invoked).
- `playwright-e2e-init` for E2E layer (optional, not auto-invoked).

## When to Use

This skill should be used when:

- Adding tests to a project without test coverage
- Setting up GitHub Actions CI/CD for the first time
- Configuring Vitest with coverage thresholds
- Initializing testing infrastructure for a new project
- Migrating from Jest to Vitest

## What It Does

1. **Detects project type** (Next.js, NestJS, React, Node.js)
2. **Adds Vitest configuration** with appropriate settings
3. **Creates test setup files** for the environment
4. **Adds GitHub Actions workflow** for CI/CD
5. **Configures 80% coverage thresholds**
6. **Adds test scripts** to package.json
7. **Installs required dependencies**

## Project Type Detection

The skill detects project type by scanning:

- `package.json` dependencies (next, @nestjs/core, react, etc.)
- Config files (next.config.*, nest-cli.json, etc.)
- Directory structure (app/, src/, pages/, etc.)

## Quick Start

Example prompt:

```
Add testing and CI/CD to this project
```

Or be specific:

```
Set up Vitest with 80% coverage and GitHub Actions for this Next.js project
```

## Configuration by Project Type

### Next.js Projects

**Dependencies installed:**

```bash
bun add -D vitest @vitest/coverage-v8 @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom
```

**Files created:**

- `vitest.config.ts` - Vitest with jsdom environment
- `src/test/setup.ts` - Test setup with RTL matchers
- `.github/workflows/ci.yml` - CI pipeline

**Test pattern:** `**/*.{test,spec}.{ts,tsx}`

### NestJS Projects

**Dependencies installed:**

```bash
bun add -D vitest @vitest/coverage-v8 supertest @types/supertest
```

**Files created:**

- `vitest.config.ts` - Vitest with node environment
- `test/setup.ts` - Test setup for NestJS
- `.github/workflows/ci.yml` - CI with MongoDB service

**Test pattern:** `src/**/*.spec.ts`

### React/Node.js Projects

Follows similar patterns based on detected framework.

## Coverage Configuration

Default thresholds (configurable):

- Lines: 80%
- Functions: 80%
- Branches: 75%
- Statements: 80%

Coverage is enforced:

1. In pre-commit hooks (via Husky)
2. In CI/CD pipeline (GitHub Actions)

## GitHub Actions Features

The generated CI workflow includes:

- Bun setup with caching
- Dependency installation
- Lint/format checking (Biome)
- TypeScript type checking
- Test execution with coverage
- Build verification
- MongoDB service (for NestJS projects)

## Templates

Templates are located in the `templates/` directory:

| Template | Purpose |
|----------|---------|
| `vitest.config.nextjs.ts` | Vitest config for Next.js |
| `vitest.config.nestjs.ts` | Vitest config for NestJS |
| `ci-nextjs.yml` | GitHub Actions for Next.js |
| `ci-nestjs.yml` | GitHub Actions for NestJS |
| `test-setup-react.ts` | Test setup with RTL |
| `test-setup-node.ts` | Test setup for Node.js |

## Monorepo Support

For monorepos (detected by workspaces in package.json):

1. Creates `vitest.workspace.ts` at root
2. Creates individual `vitest.config.ts` per package
3. Creates root-level GitHub Actions workflow
4. Uses `bun --filter '*' test` for orchestration

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `husky-test-coverage` | Adds pre-commit coverage enforcement |
| `linter-formatter-init` | Works alongside for code quality |
| `playwright-e2e-init` | Adds E2E testing after unit tests |
| `testing-expert` | Provides testing patterns guidance |

## Example Usage

### Adding tests to a Next.js project

```
User: Add testing to this project

Agent:
1. Detects Next.js from package.json
2. Installs vitest, @vitest/coverage-v8, @testing-library/react
3. Creates vitest.config.ts with jsdom environment
4. Creates src/test/setup.ts
5. Creates .github/workflows/ci.yml
6. Adds test scripts to package.json
```

### Adding tests to a NestJS API

```
User: Set up tests for this NestJS API

Agent:
1. Detects NestJS from @nestjs/core dependency
2. Installs vitest, @vitest/coverage-v8, supertest
3. Creates vitest.config.ts with node environment
4. Creates test/setup.ts
5. Creates .github/workflows/ci.yml with MongoDB service
6. Adds test scripts to package.json
```

## Troubleshooting

### Tests not finding modules

Ensure path aliases in `vitest.config.ts` match `tsconfig.json`:

```typescript
resolve: {
  alias: {
    "@": path.resolve(__dirname, "./src"),
  },
},
```

### Coverage below threshold

1. Check coverage report: `bun test --coverage`
2. Identify uncovered lines
3. Add tests or adjust thresholds temporarily

### CI failing on type errors

Ensure `bunx tsc --noEmit` passes locally before pushing.

## Best Practices

1. **Start with unit tests** for utilities and services
2. **Add integration tests** for API endpoints
3. **Use E2E tests sparingly** for critical flows
4. **Run tests before commits** via Husky
5. **Monitor coverage trends** in CI
