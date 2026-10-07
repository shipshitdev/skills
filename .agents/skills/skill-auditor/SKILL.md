---
name: skill-auditor
description: |
  Audit the skills library for duplicates, stale content, spec violations, and structural issues.
  Run periodically or before releases.
metadata:
  internal: true
  version: "2.2.4"
  tags: "audit, skills, quality, maintenance"
---

# Skill Auditor

Comprehensive audit of the skills library for quality and consistency.

## Audit Modes

| Mode | Scope | Command |
|---|---|---|
| `skills` (default) | Public skills, commands, bundles, and catalog sync | Follow the categories below |
| `routines` | Local Claude scheduled tasks and Codex automations | `python3 scripts/audit-routines.py` |

Routine mode follows
`.agents/memory/system/routine-standards.md`. It is read-only: detect normalized
duplicate bodies and prompt-level model, effort, schedule, cwd/workspace/worktree,
and environment leakage. Report source identifiers and field names only; never print
prompt bodies, environment values, or TOML values. Use `--show-paths` only when the
caller explicitly wants local paths in the report.

## Audit Categories

### 1. Duplicate Detection

Find skills that overlap and should be consolidated:

- Compare descriptions for semantic similarity
- Check for skills with near-identical `when_to_use` triggers
- Flag naming collisions (e.g., `react-patterns` vs `react-refactor`)

### 2. Spec Compliance

For each SKILL.md, check:

- Frontmatter follows Agent Skills spec (see `.agents/memory/system/skill-standards.md`)
- `version`/`tags` inside `metadata:` block, not top-level
- No forbidden fields (`auto_activate`, `auto_trigger`, `risk`)
- `metadata.tags` is a comma-separated string, not YAML list
- No harness-owned execution parameters in reusable content; apply
  `.agents/memory/system/execution-boundary.md` to skills, commands, and routine
  templates

### 3. Structural Issues

- Orphaned nested directories (`skills/<name>/<name>/`)
- Empty skill directories (no SKILL.md)
- Skills in README that no longer exist in filesystem
- Skills in filesystem that are missing from README
- Broken references to non-existent files in skill content

### 4. Content Quality

- Empty or placeholder descriptions
- Hardcoded project-specific paths (`/workspace/`, `@genfeedai/`)
- Escaped backtick fences (`\`\`\``) instead of real fences
- Skills that reference scripts not bundled with the skill

### 5. README Sync

Compare the `skills/` directory listing against the README's categorized skill
lists (backticked names under the `## Skills (N)` heading — the README has no
per-skill link table):

```bash
# Get skills from filesystem
REPO_TMP="$(git rev-parse --show-toplevel)/.tmp"
mkdir -p "$REPO_TMP"
find skills -maxdepth 1 -mindepth 1 -type d | sed 's|skills/||' | sort > "$REPO_TMP/fs-skills.txt"

# Get skills from the README's categorized lists
sed -n '/^## Skills (/,/^## How Skills Adapt/p' README.md \
  | grep -oE '`[a-z0-9-]+`' | tr -d '`' | sort -u > "$REPO_TMP/readme-skills.txt"

# Diff
comm -23 "$REPO_TMP/fs-skills.txt" "$REPO_TMP/readme-skills.txt"  # in fs, not README
comm -13 "$REPO_TMP/fs-skills.txt" "$REPO_TMP/readme-skills.txt"  # in README, not fs
```

Also verify each category heading's `(N)` count matches the number of names in
its list. A skill may appear in more than one category, so the per-category
sum exceeding the total is expected.

## Output Format

Report findings as a table:

| Skill | Issue | Severity | Action |
|-------|-------|----------|--------|
| `code-refactoring-refactor-clean` | Duplicate of `refactor-code` | HIGH | Merge |
| `spec-to-code-compliance` | Empty directory | HIGH | Delete |
| `skill-capture` | tags as YAML list | MEDIUM | Fix to string |

For routine mode, report totals, leakage categories, anonymous source identifiers,
duplicate-family groups, and observed app-owned field names. Do not include the
matched text or configuration values.
