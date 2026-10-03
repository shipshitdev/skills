# Repository Architecture

last_verified: 2026-07-13

## Directory Map

<!-- catalog-layout:start -->
| Path | Role | Generated fact |
|---|---|---|
| `.agents/` | Repository memory, standards, and maintenance skills | Tracked |
| `.claude/` | Claude loader adapters for shared maintenance content | Tracked |
| `.claude-plugin/` | Generated Claude marketplace catalog | 199 generated plugins |
| `.codex/` | Codex loader adapters for shared maintenance content | Tracked |
| `.github/` | Issue templates and GitHub Actions workflows | Tracked |
| `.husky/` | Git hook configuration | Tracked |
| `.tmp/` | Tracked repository content | Tracked |
| `assets/` | Static repository assets | Tracked |
| `bundles/` | Generated marketplace bundle snapshots | 13 generated bundles |
| `commands/` | Claude Code/plugin command adapters | 30 command adapters |
| `docs/` | Human-facing orientation pages for flagship skills | Tracked |
| `prompts/` | Shared prompt resources | Tracked |
| `resources/` | Authoring references and supporting documentation | Tracked |
| `scripts/` | Validation, generation, migration, and audit tooling | Tracked |
| `skills/` | Canonical public Agent Skills sources | 186 canonical skills |
| `upstream/` | Pinned upstream snapshots and reviewed adaptation ledgers | Tracked |
<!-- catalog-layout:end -->

## Data Flow

```
skills/*/SKILL.md ─┐
commands/*.md      ├─→ scripts/generate-catalog-summary.js ─→ catalog.json + marked docs
bundle definitions ┘
skills/<name>/SKILL.md    ──→  scripts/generate-marketplace-bundles.js  ──→  bundles/<name>/
skills/<name>/plugin.json ──→  copied into bundle snapshots
catalog.json + skills/    ──→  scripts/generate-marketplace-json.js     ──→  .claude-plugin/marketplace.json
```

All generation is triggered by: `bun run marketplace:generate`

CI auto-runs on push to master when `skills/**`, `commands/**`, or scripts change.

## Skill Anatomy

```yaml
---
name: skill-name           # Must match directory name
description: >-            # 1-1024 chars, front-loaded use case
  What this skill does.
metadata:
  version: "1.0.0"         # Semver string
  tags: "tag1, tag2"       # Comma-separated string (NOT list)
  author: "author-name"
---

# Skill Title

[Imperative, platform-neutral instructions...]
```

Required: `name`, `description`, `SKILL.md`, `plugin.json`
Optional: `license`, `compatibility`, `when_to_use`, `allowed-tools`, `context`

## Bundle Structure

<!-- catalog-bundles:start -->
13 generated bundles: `ai-agents`, `backend`, `dev-loop`, `dev-workflow`, `frontend`, `github`, `infrastructure`, `payments`, `planning`, `security`, `session`, `testing`, `workspace`.
<!-- catalog-bundles:end -->

Each bundle = curated subset of skills for a domain. Defined in `scripts/plugin-categories.json`.

## Validation Pipeline

1. **Pre-commit hook** (`.husky/`): runs `validate-changed-skills.sh` on modified skills
2. **Local full validation**: `bun run validate` → `validate-skill-sync.sh`
3. **Lint**: `bun run lint` (markdownlint, Biome, shellcheck)
4. **CI**: GitHub Actions validates, audits, then regenerates bundles + marketplace on master push
