---
name: agent-config-audit
description: Audits agent instruction files (AGENTS.md, CLAUDE.md, hooks, settings) across workspaces, report-only. Use when configs drift, rules duplicate, or files go stale.
metadata:
  version: "2.2.4"
  tags: "audit, claude-md, agents-md, config, documentation, maintenance"
when_to_use: "stale cursorrules, sync agent configs"
---

# Agent Config Audit

Audit the instruction and config files that steer coding agents. Default mode is report-only; loading this skill grants no authority to edit files. Honor the caller's scope and limits, and ask before expanding them.

## When to use

- The user says "audit CLAUDE.md", "agent config", "rules out of date", "config drift", or "sync docs".
- After restructuring repos, adding or removing projects, or changing conventions.
- As periodic maintenance (monthly is reasonable).
- Agents keep making the same mistake despite rules existing (a sign of stale or contradictory config).
- After a refactor that changed file paths, package names, or architecture.

## When not to use

- Application defects: debug them instead.
- Capturing a single new rule from the conversation: just add it to the right file.
- Auditing code quality rather than agent configuration: use a code audit/review skill.
- Setting up or repairing formatter/linter config.
- Scaffolding an `.agents/` folder from scratch: use an agent-folder-init skill if available.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Workspace root | Yes | Directory containing the repos (default: current directory) |
| Scope | No | `full` (all checks) or one of `dedup`, `stale`, `instructions`, `cursor`, `settings` |
| Mode | No | `report` (default, read-only) or `fix` |

## Guardrails

- Report mode makes no file changes, pushes nothing, and calls no external APIs.
- Never infer fix mode from findings or from a request to "sync" configs. Enter fix mode only when the user explicitly asks for mutation, show the exact files and operations first, and get confirmation.
- Get confirmation before overwriting existing agent configs and before deleting or consolidating duplicated rules.

## Workflow

### Step 1: Inventory

Find every agent config file in the workspace, including sub-repos:

```bash
glob "**/CLAUDE.md"
glob "**/AGENTS.override.md"
glob "**/AGENTS.md"
glob "**/.cursorrules"
glob "**/.cursor/rules"
glob "**/.claude/settings.json"
glob "**/.claude/settings.local.json"
glob "**/.claude/hooks.json"
glob "**/.agents/memory/*.md"
```

Build an inventory table:

```
| Layer              | Files Found | Total Lines |
|--------------------|-------------|-------------|
| CLAUDE.md          | N           | N           |
| AGENTS.override.md | N           | N           |
| AGENTS.md          | N           | N           |
| Configured fallbacks | N         | N           |
| .cursorrules       | N           | N           |
| .claude/ config    | N           | N           |
| .agents/memory/    | N           | N           |
```

### Step 2: Dedup check

Search all config files for rules that commonly appear in several places, such as:

- `any` types / "No any" (belongs in AGENTS.md plus hooks only)
- `console.log` / logger rules (AGENTS.md only)
- Conventional commits (AGENTS.md only)
- AbortController usage (AGENTS.md or one linked memory topic)
- Session file naming (hooks plus one doc reference)
- Import order (AGENTS.md or a coding-standards topic)
- Soft delete flags and multi-tenancy scoping (one data/security topic each)

Adapt the list to the repo's own recurring rules. For each rule, count occurrences, for example:

```
grep "No \`any\`\|NO \`any\`\|no any types" across all config files
```

Healthy target: each rule appears in at most 2 files (one "teach" doc plus one runtime enforcement such as a hook). Flag any rule appearing 3+ times.

### Step 3: Staleness check

```bash
# Files with old "Last Updated" dates (> 90 days)
grep -r "Last Updated:" across .cursorrules, .cursor/rules

# Hardcoded absolute workspace paths that should be relative
grep -rE "/(Users|home)/" across .agents/ and config files

# References to directories that no longer exist
# Compare referenced paths against the actual directory listing
```

Flag: any "Last Updated" more than 90 days behind the current date; any hardcoded absolute path; any reference to a directory that does not exist.

### Step 4: Codex instruction resolution (only if the repo uses Codex)

Read the effective `.codex/config.toml` and record `project_doc_fallback_filenames` plus any runtime policy before judging the chain. Then check:

- [ ] Each directory resolves at most one nonempty instruction file in this order: `AGENTS.override.md`, `AGENTS.md`, then configured fallback filenames
- [ ] The chain is read from the project root down to the working directory
- [ ] `AGENTS.override.md` is used only where a subtree intentionally replaces the same-directory `AGENTS.md`
- [ ] `AGENTS.md` contains repo-specific rules and entry points
- [ ] Any fallback filenames are explicitly declared in the effective `.codex/config.toml`
- [ ] Runtime approval, sandbox, and network policy lives in the effective `.codex/config.toml` or hooks, not in assumed prose
- [ ] No `.codex/instructions.md` file or `.codex/commands` directory is presented as a supported Codex entry surface

Flag: undocumented fallback files, accidental overrides, instruction files that contradict runtime configuration, and unsupported `.codex/instructions.md` or `.codex/commands` surfaces.

### Step 5: AGENTS.md consistency

For each AGENTS.md:

- [ ] Has repo-specific context (not just a generic "docs in .agents/" pointer)
- [ ] Links to `.agents/` paths that actually exist
- [ ] Structure is consistent across repos

Flag any pure generic stub (under 20 lines with no repo-specific content).

### Step 6: Cursor config

For `.cursorrules` and `.cursor/rules`:

- [ ] No emoji in headers (wastes tokens)
- [ ] "Last Updated" within 90 days
- [ ] Project paths reference actual directories
- [ ] No duplicated session-file rules (hooks already handle this)

### Step 7: Settings

For `.claude/settings.json` and `.claude/settings.local.json`:

- [ ] Denied skills have a documented rationale (SETTINGS-NOTES.md or equivalent)
- [ ] Local bash overrides do not contradict documented standards without explanation
- [ ] No stale tool references

### Step 8: Report

```markdown
# Agent Config Audit Report
**Date:** YYYY-MM-DD
**Workspace:** [path]
**Files Scanned:** N

## Summary
- Critical issues: N
- Moderate issues: N
- Minor issues: N
- Total config lines: N (target: reduce by dedup)

## Critical: Rule Duplication
| Rule | Occurrences | Files | Target |
|------|-------------|-------|--------|
| "No any types" | 6 | [list] | 2 |

## Critical: Stale Files
| File | Last Updated | Days Stale |
|------|-------------|------------|

## Moderate: Instruction Resolution Drift
| Workspace | Override | AGENTS.md | Configured Fallbacks | Runtime Policy Location |
|-----------|----------|-----------|----------------------|-------------------------|

## Moderate: Stub AGENTS.md
| File | Lines | Has Repo Context |
|------|-------|------------------|

## Minor: Emoji in Config
| File | Emoji Count |
|------|-------------|

## Recommendations
1. [Specific actionable fix]
2. [Specific actionable fix]
```

### Step 9: Apply fixes (fix mode only)

After explicit request and confirmation of the exact plan, apply these principles:

- Each rule lives in ONE canonical location.
- Hooks enforce at runtime; docs teach, not repeat.
- Strip emoji from all config files.
- Update all "Last Updated" dates.
- Replace hardcoded paths with relative references.
- Consolidate project instructions into AGENTS.md and scoped AGENTS.override.md files.
- Move runtime approval, sandbox, and network policy into the effective `.codex/config.toml` or hooks.

## Reference files

- `references/canonical-ownership.md`: which rule belongs in which file
- `references/healthy-config-example.md`: example of a well-structured config set

## Anti-patterns

| DON'T | DO | Why |
|-------|-----|-----|
| Repeat the same rule in AGENTS.md, CLAUDE.md, `.agents/memory/`, and hooks | Put the rule in ONE canonical file; others reference it | Duplication wastes context tokens and drifts when one copy is updated |
| Leave an old "Last Updated" date in a file you changed | Update dates when modifying any config file | Stale dates erode trust in the config system |
| Create an extra instruction filename without configuring it | Put shared guidance in AGENTS.md; use AGENTS.override.md for scoped overrides; declare any genuine fallback in the effective `.codex/config.toml` | Codex resolves native instruction names plus explicitly configured fallbacks |
| Use emoji in config headers | Use plain text headers | Emoji waste tokens on every context load |
| Hardcode `/Users/username/path/` in config files | Use relative paths or describe the location generically | Hardcoded paths break when the workspace moves or another developer joins |
| Recreate a parallel legacy instruction tree under `.agents/` | Put durable guardrails in topic files under `.agents/memory/` and shared actionable rules in AGENTS.md | Keeps durable context discoverable without parallel hierarchies |

## Validation

After the audit, confirm:

- [ ] No rule appears in more than 2 config files
- [ ] All `.cursorrules` files have "Last Updated" within 90 days
- [ ] Every Codex instruction file is native (`AGENTS.override.md` or `AGENTS.md`) or an explicitly configured fallback
- [ ] Runtime approval, sandbox, and network claims match the effective `.codex/config.toml` or hooks
- [ ] No hardcoded absolute paths in any config file
- [ ] No emoji in `.cursorrules` or `.cursor/rules` headers
- [ ] Denied skills in settings.json have a documented rationale
- [ ] Total config line count decreased or stayed flat

## Contract

Inputs:

- Workspace root
- Scope: full, dedup, stale, instructions, cursor, settings, or fix
- Optional list of repos/config files to include

Outputs:

- Audit report with critical/moderate/minor findings
- Proposed fix plan
- Applied changes only when fix mode is explicit

Creates/Modifies:

- Report mode: no file changes
- Fix mode: agent config files, `.agents/` docs, and related settings, but only
  after an explicit fix request and confirmation of the exact plan

External Side Effects:

- None by default
- Does not push, publish, or call external APIs

Confirmation Required:

- Before entering fix mode or using any mutating file/shell operation; an audit or
  sync request alone authorizes report mode only
- Before overwriting existing agent configs
- Before deleting or consolidating duplicated rules

Delegates To:

- `rules-capture` for single new preferences
- `agent-folder-init` for missing `.agents/` structure
