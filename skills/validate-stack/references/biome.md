# Biome 2.3+ validator reference

Checks, deprecated patterns, and examples for the `biome` stack of `scripts/validate.py --stack biome`.

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

See the Full guide section below (§ What Gets Checked, § Biome 2.3+ Features, § Recommended Configuration) for full GOOD/BAD config examples and a complete recommended `biome.json`.

## Deprecated Patterns

| Deprecated | Replacement (2.3+) |
|------------|-------------------|
| `organizeImports.enabled` | `assist.actions.source.organizeImports` |
| Schema < 2.0 | Schema 2.3.11+ |
| `@biomejs/biome` < 2.3 | `@biomejs/biome@latest` |
| No domains config | Use `linter.domains` for frameworks |

See the Full guide section below (§ Validation Output) for a sample validation report.

## Migration from ESLint

1. Remove ESLint/Prettier packages, add `@biomejs/biome@latest`
2. Generate config: `bunx biome init`
3. Port existing rules: `bunx biome migrate eslint --write`
4. Update `package.json` lint/format scripts to call `biome`
5. Delete old `.eslintrc*` / `.prettierrc*` / `.eslintignore` / `.prettierignore`

See the Full guide section below (§ Migration from ESLint) for the exact commands per step, plus VS Code editor settings and a CI/CD workflow snippet.

## Full guide

### What Gets Checked

#### 1. Biome Version & Schema

**GOOD - Biome 2.3+:**

```json
{
  "$schema": "https://biomejs.dev/schemas/2.3.12/schema.json"
}
```

**BAD - Old schema:**

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json"
}
```

#### 2. Package Version

```json
// GOOD: v2.3+
"@biomejs/biome": "^2.3.0"

// BAD: v1.x or v2.0-2.2
"@biomejs/biome": "^1.9.0"
```

#### 3. Linter Configuration

**GOOD - Biome 2.x:**

```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  }
}
```

#### 4. Biome Assist (2.0+)

**GOOD - Using assist:**

```json
{
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on"
      }
    }
  }
}
```

**BAD - Old organizeImports location:**

```json
{
  "organizeImports": {
    "enabled": true
  }
}
```

#### 5. Domains (2.0+)

**GOOD - Using domains for framework-specific rules:**

```json
{
  "linter": {
    "domains": {
      "react": "on",
      "next": "on"
    }
  }
}
```

#### 6. Suppression Comments

**GOOD - Biome 2.0+ comments:**

```typescript
// biome-ignore lint/suspicious/noExplicitAny: legacy code
// biome-ignore-all lint/style/useConst
// biome-ignore-start lint/complexity
// biome-ignore-end
```

**BAD - Wrong format:**

```typescript
// @ts-ignore  // Not Biome
// eslint-disable  // Wrong tool
```

### Biome 2.3+ Features

#### Type-Aware Linting

Biome 2.0+ includes type inference without requiring TypeScript compiler:

```json
{
  "linter": {
    "rules": {
      "correctness": {
        "noUndeclaredVariables": "error",
        "useAwaitThenable": "error"
      }
    }
  }
}
```

#### Assist Actions

```json
{
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on",
        "useSortedKeys": "on"
      }
    }
  }
}
```

#### Multi-file Analysis

Lint rules can query information from other files.

#### Framework Domains

```json
{
  "linter": {
    "domains": {
      "react": "on",       // React-specific rules
      "next": "on",        // Next.js rules
      "test": "on"         // Testing framework rules
    }
  }
}
```

### Recommended Configuration

```json
{
  "$schema": "https://biomejs.dev/schemas/2.3.12/schema.json",
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on"
      }
    }
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noForEach": "off"
      },
      "style": {
        "noNonNullAssertion": "off"
      },
      "suspicious": {
        "noArrayIndexKey": "off",
        "noExplicitAny": "warn"
      },
      "correctness": {
        "useAwaitThenable": "error",
        "noLeakedRender": "error"
      }
    },
    "domains": {
      "react": "on",
      "next": "on"
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "es5",
      "semicolons": "always"
    }
  },
  "files": {
    "ignore": [
      "node_modules",
      "dist",
      "build",
      ".next",
      "out",
      ".cache",
      ".turbo",
      "coverage"
    ]
  }
}
```

### Validation Output

```
=== Biome 2.3+ Validation Report ===

Package Version: @biomejs/biome@2.3.11 ✓

Configuration:
  ✓ Schema version: 2.3.11
  ✓ Linter enabled with recommended rules
  ✓ Using assist.actions for imports
  ✗ No domains configured (consider enabling react, next)
  ✓ Formatter configured

Rules:
  ✓ noExplicitAny: warn
  ✓ useAwaitThenable: error
  ✗ noLeakedRender not enabled (recommended)

Summary: 2 issues found
```

### Migration from ESLint

#### Step 1: Install Biome

```bash
bun remove eslint prettier eslint-config-* eslint-plugin-*
bun add -D @biomejs/biome@latest
```

#### Step 2: Create biome.json

```bash
bunx biome init
```

#### Step 3: Migrate rules

```bash
bunx biome migrate eslint --write
```

#### Step 4: Update scripts

```json
{
  "scripts": {
    "lint": "biome lint .",
    "lint:fix": "biome lint --write .",
    "format": "biome format --write .",
    "check": "biome check .",
    "check:fix": "biome check --write ."
  }
}
```

#### Step 5: Remove old configs

```bash
rm .eslintrc* .prettierrc* .eslintignore .prettierignore
```

### VS Code Integration

```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "editor.codeActionsOnSave": {
    "source.organizeImports.biome": "explicit",
    "quickfix.biome": "explicit"
  }
}
```

### CI/CD Integration

```yaml
# .github/workflows/lint.yml
- name: Validate Biome Config
  run: |
    python3 scripts/validate.py \
      --root . \
      --strict \
      --ci

- name: Lint
  run: bunx biome check --error-on-warnings .
```
