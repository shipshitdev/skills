---
name: skill-validator
description: |
  Validate SKILL.md files against the Agent Skills spec and Claude Code extensions.
  Run on new or modified skills before committing.
metadata:
  internal: true
  version: "2.2.3"
  tags: "validation, skills, spec-compliance, quality"
---

# Skill Validator

Validate SKILL.md files against the Agent Skills specification and Claude Code extensions.

## When to Run

- After creating a new skill
- After modifying a skill's SKILL.md frontmatter
- Before committing skill changes
- During periodic repo audits

## Validation Rules

### Required Fields (Agent Skills Spec)

Every SKILL.md must have YAML frontmatter with:

- `name` — kebab-case, matches directory name
- `description` — 1-3 sentences, under 1024 chars, starts with verb or domain noun

### Metadata Block

`version` and `tags` must be inside `metadata:`, never top-level:

```yaml
# CORRECT
metadata:
  version: "1.0.0"
  tags: "react, performance, optimization"

# WRONG — top-level version
version: 1.0.0

# WRONG — tags as YAML list
metadata:
  tags:
    - react
    - performance
```

### Forbidden Fields

These are not part of any spec:

- `auto_activate` / `auto_trigger` — removed in 2026-04 migration
- `risk` — not in Agent Skills or Claude Code specs

### Claude Code Extensions (Optional)

Valid extension fields (must match `allowed_fields` in `scripts/validate-skill-sync.sh`):

| Field | Purpose |
|-------|---------|
| `when_to_use` | Extra trigger phrases appended to `description` |
| `disable-model-invocation` | Prevent auto-triggering (for destructive skills) |
| `user-invocable` | `false` hides from the `/` menu |
| `allowed-tools` | Auto-approve **allowlist** (not a sandbox — unlisted tools stay callable) |
| `disallowed-tools` | Removes tools from the pool while active (the actual block mechanism) |
| `argument-hint` | Autocomplete hint for expected arguments |
| `compatibility` | Environment prerequisites (packages, network, target agent) |
| `context` | `fork` for subagent isolation |
| `agent` | Subagent type when `context: fork` |
| `hooks` | Lifecycle hooks scoped to the skill |
| `paths` | ⚠️ Broken upstream (#49835) — flag if present |
| `shell` | `bash` (default) or `powershell` |

### Forbidden Fields (updated)

- `auto_activate` / `auto_trigger` — removed in 2026-04 migration
- `risk` — not in any spec
- `metadata.triggers` — duplicate activation metadata; put trigger phrases in
  `description` or `when_to_use`
- `model` / `effort` — recognized by Claude Code but owned by app/session
  configuration, not public reusable skills
- Any top-level field not in the tables above → "Unsupported top-level frontmatter field"

### Content Rules

- No hardcoded `/workspace/` paths
- No tool names in instructions (say "search for" not "use Grep")
- Imperative/infinitive style ("Configure X" not "You should configure X")
- Code blocks use real backtick fences, not escaped `\`\`\``
- **No concrete model names** in body, `references/`, or `scripts/` — reject tier+version IDs (`claude-3-7-sonnet-20250219`, `claude-opus-4.5`, `gpt-5.5`), dated snapshots, and bare family names used as routing keys. Exception: orchestrator skills may name **capability tiers** in prose. See [skill-standards.md → Model references](../memory/system/skill-standards.md).
- **No harness-owned execution parameters** in skills, commands, or routine templates.
  Apply [execution-boundary.md](../memory/system/execution-boundary.md).
- **Routine templates** follow
  [routine-standards.md](../memory/system/routine-standards.md). Run
  `python3 scripts/audit-routines.py` to detect duplicate bodies and app-parameter
  leakage without printing prompt or configuration values.
- **Provenance (derived skills only):** when `metadata.source` is set, `metadata.last_synced` and a README `## Upstream` section are required (enforced by `check_provenance()`). In-house skills need no provenance fields.

## Validation Process

1. Read the SKILL.md frontmatter
2. Check `name` matches parent directory name
3. Check `description` exists and is under 1024 chars
4. Check `description` plus `when_to_use` is under 1536 chars
5. Check `plugin.json` description is present and under 100 chars
6. Check `version`/`tags` are NOT top-level (must be inside `metadata:`)
7. Check for forbidden fields (`auto_activate`, `auto_trigger`, `risk`, `model`, `effort`, any field not in the extension tables)
8. Check for escaped backtick fences in content
9. Validate frontmatter value types: `allowed-tools` is a scalar,
   `metadata.version` and `metadata.tags` are quoted scalars, and `metadata` is a map
10. Reject duplicate `metadata.triggers`; keep activation guidance in `description`
    or `when_to_use`
11. Check for hardcoded paths (`/workspace/`, project-specific paths)
12. Grep body + `references/` + `scripts/` for concrete model names (`claude-*`, `gpt-*`, `sonnet`/`opus`/`haiku` used as IDs); allow only capability-tier prose in orchestrator skills
13. Warn when skills, commands, or templates set harness-owned execution parameters
14. Warn when a side-effecting skill lacks both `disable-model-invocation: true`
    and an explicit `Confirmation Required` gate
15. Check prose routing references across the body, excluding frontmatter and code
    fences, and flag missing local skills
16. Check provenance for derived skills: if `metadata.source` is set, require `metadata.last_synced` and a README `## Upstream` section
17. Run `bunx markdownlint-cli` on the file
18. Run `./scripts/validate-skill-sync.sh` for cross-validation

## Quick Validation Command

```bash
# Single skill
bunx markdownlint-cli skills/<name>/SKILL.md skills/<name>/references/*.md

# All skills
bunx markdownlint-cli --ignore bundles --ignore dist "**/*.md"

# Sync validation
./scripts/validate-skill-sync.sh
```
