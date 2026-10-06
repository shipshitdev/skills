---
name: husky-test-coverage
description: Sets up or verifies Husky pre-commit hooks that enforce test coverage above 80% (configurable) for Node/TypeScript projects using Vitest (or Mocha with nyc/c8).
metadata:
  version: "2.2.2"
  tags: "husky, testing, coverage"
when_to_use: "coverage threshold, pre-commit tests"
---

# Husky Test Coverage

Set up or verify Husky git hooks to ensure tests run and coverage thresholds are enforced on every commit.

## Contract

Inputs:

- Target repository, setup or verification mode, and coverage threshold

Outputs:

- Coverage setup plan, applied hook/configuration changes, or a verification report

Creates/Modifies:

- Hooks, package scripts, dependencies, and coverage configuration only in setup mode

External Side Effects:

- Dependency installs and test execution within the authorized setup and host limits

Confirmation Required:

- A verification request stays read-only. Obtain explicit setup authorization before changing hooks, dependencies, or thresholds
- Loading the skill grants no additional authority. Existing explicit approval
  applies only to the same target and actions; preserve report-only restrictions.

Delegates To:

- None

## When to Use

- Setting up test coverage enforcement for the first time
- Verifying existing Husky/test setup is correctly configured
- Configuring pre-commit hooks for test coverage
- Adapting coverage setup to different test runners

## Project Context Discovery

1. **Check package.json:**
   - Review existing test scripts
   - Detect test runner from dependencies (vitest, mocha)
   - Check for existing Husky installation
   - Review existing coverage configuration

2. **Identify Test Runner:**
   - Vitest: Check for `vitest` in dependencies, look for `vitest.config.ts` or `vitest.config.js`; check `@vitest/coverage-v8` is installed
   - Mocha: Check for `mocha` in dependencies, check for coverage tool (nyc, c8)

3. **Check Coverage Configuration:**
   - Vitest: Look for `test.coverage.thresholds` in vitest.config.*
   - Mocha: Look for `.nycrc.json` or coverage config in package.json

4. **Verify Existing Husky Setup:**
   - Check if `.husky/` directory exists
   - Review existing pre-commit hook
   - Check if Husky is in package.json dependencies

5. **Detect Test Files:**
   - Scan for `*.test.*` or `*.spec.*` files
   - Verify tests exist before enforcing coverage

## Quick Start

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py --root /path/to/project
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py --root /path/to/project --dry-run
```

See `references/full-guide.md` (§ Quick Start Examples) for threshold, warn-only, and skip-if-no-tests invocations.

## What Gets Configured

### Husky Setup

- Installs Husky if not already present
- Initializes Husky (`bunx husky install`)
- Creates `.husky/pre-commit` hook that runs tests with coverage
- Adds `prepare` script to package.json (if missing)

### Test Runner Detection

The skill automatically detects:

- **Vitest**: Uses `vitest run --coverage` in pre-commit hook
- **Mocha**: Uses `nyc` or `c8` with mocha test command

### Coverage Configuration

**Vitest:**

- Creates `vitest.config.ts/js` with `test.coverage.thresholds` when none exists; prints the snippet when a config already exists
- Configures the `v8` coverage provider and installs `@vitest/coverage-v8` when missing
- Default thresholds: 80% lines, 75% branches, 80% functions, 80% statements

**Mocha + nyc:**

- Creates or updates `.nycrc.json` with coverage thresholds
- Configures text, html, and lcov reporters

### Pre-commit Hook

The created hook:

- Runs tests with coverage before every commit
- Fails the commit if coverage is below threshold (configurable)
- Can skip if no test files are found (optional)

## Configuration Options

### Command Line Arguments

- `--root <path>`: Project root directory (required)
- `--threshold <number>`: Coverage threshold percentage (default: 80)
- `--fail-on-below`: Fail commit if coverage below threshold (default: true)
- `--no-fail-on-below`: Allow commit even if coverage below threshold
- `--skip-if-no-tests`: Skip hook if no test files found
- `--dry-run`: Show what would be done without making changes

### Configuration File

Create `.husky-test-coverage.json` in project root. See `references/full-guide.md` (§ .husky-test-coverage.json Example) for the full schema.

### Package.json Configuration

Alternatively, add to `package.json`:

```json
{
  "huskyTestCoverage": {
    "threshold": 80,
    "failOnBelow": true
  }
}
```

## Tech Stack Adaptation

### Vitest Projects

**Detection:**

- Checks for `vitest` in dependencies
- Looks for `vitest.config.ts` or `vitest.config.js`

**Configuration:**

- Updates or creates Vitest config with `test.coverage.thresholds` (provider `v8`, package `@vitest/coverage-v8`)
- Pre-commit hook: `bunx vitest run --coverage`

See `references/full-guide.md` (§ Example vitest.config.ts) for a full config example.

### Mocha Projects

**Detection:**

- Checks for `mocha` in dependencies
- Checks for coverage tool (`nyc` or `c8`)

**Configuration:**

- Creates or updates `.nycrc.json` for nyc
- Pre-commit hook: `nyc --reporter=text --reporter=html bun run test`

See `references/full-guide.md` (§ Example .nycrc.json) for a full config example.

## Package Manager Support

The skill automatically detects and uses:

- **bun**: `bun run test` (preferred)
- **yarn**: `yarn test`
- **pnpm**: `pnpm run test`

## Workflow

1. Scan package.json for test runner, dependencies, existing Husky config, and coverage config files. Verify test files exist.
2. Identify Vitest or Mocha; detect coverage tool (built-in or nyc/c8); determine package manager.
3. Install Husky if missing; initialize hooks; add `prepare` script if needed.
4. Create or update coverage configuration; set thresholds (default 80%); configure reporters.
5. Generate pre-commit hook script; set enforcement behavior (block or warn).
6. Verify setup; test hook with a commit; adjust thresholds if needed.

## Integration with Other Skills

| Skill | How It Works Together |
|-------|----------------------|
| **project-init-orchestrator** | Auto-invoked after scaffolding; sets Vitest + 80% threshold + CI/CD. Run this skill separately only when adding to an existing project. |
| **linter-formatter-init** | Both configure Husky; this skill covers test coverage, linter-formatter-init covers linting/formatting |
| **testing-expert** | Uses testing patterns and coverage targets from testing-expert skill |

### Manual Integration (existing projects)

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py \
  --root /path/to/project \
  --threshold 80
```

## Troubleshooting

### Pre-commit hook not running

```bash
# Reinstall Husky
bunx husky install
chmod +x .husky/pre-commit
```

### Coverage not being checked

- Verify test command includes coverage flag
- Check coverage configuration file exists and is correct
- Ensure the coverage tool is installed (`@vitest/coverage-v8` for Vitest, nyc/c8 for Mocha)

### Hook fails even when tests pass

- Check coverage thresholds are achievable
- Review coverage report to see what's below threshold
- Consider adjusting thresholds or improving test coverage

### Tests run but coverage not enforced

- Verify coverage configuration file has correct thresholds
- Check test runner supports coverage (Vitest needs `@vitest/coverage-v8`, Mocha needs nyc/c8)
- Review pre-commit hook script for correct command

### Multiple test runners detected

The skill uses the first detected runner in priority order: Vitest > Mocha

## Resources

- Husky Documentation: https://typicode.github.io/husky/
- Vitest Coverage: https://vitest.dev/guide/coverage
- nyc (Istanbul): https://github.com/istanbuljs/nyc
