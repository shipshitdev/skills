# Husky Test Coverage — Full Examples

## Quick Start Examples

```bash
# Basic setup (80% coverage threshold, blocks commits below threshold)
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py \
  --root /path/to/project

# Custom threshold (85%)
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py \
  --root /path/to/project \
  --threshold 85

# Warn only (don't block commits)
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py \
  --root /path/to/project \
  --no-fail-on-below

# Skip if no tests found
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py \
  --root /path/to/project \
  --skip-if-no-tests

# Dry run to preview changes
python3 ${CLAUDE_SKILL_DIR}/scripts/setup-husky-coverage.py \
  --root /path/to/project \
  --dry-run
```

## Example vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 80,
        statements: 80
      }
    }
  }
})
```

## .husky-test-coverage.json Example

```json
{
  "coverageThreshold": {
    "lines": 80,
    "branches": 75,
    "functions": 80,
    "statements": 80
  },
  "failOnCoverageBelowThreshold": true,
  "skipIfNoTests": false
}
```

## Example .nycrc.json

```json
{
  "check-coverage": true,
  "lines": 80,
  "branches": 75,
  "functions": 80,
  "statements": 80,
  "reporter": ["text", "text-summary", "html", "lcov"]
}
```
