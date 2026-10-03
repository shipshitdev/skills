---
name: agent-config-audit
description: Audits agent instruction files (AGENTS.md, CLAUDE.md, hooks, settings) across workspaces, report-only. Use when configs drift, rules duplicate, or files go stale.
metadata:
  version: "2.2.2"
  tags: "audit, claude-md, agents-md, config, documentation, maintenance"
when_to_use: "stale cursorrules, sync agent configs"
---

# Agent Config Audit

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

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

## When to Use

- User mentions: "audit CLAUDE.md", "agent config", "rules out of date", "config drift", "sync docs"
- After restructuring repos, adding/removing projects, or changing conventions
- Periodic maintenance (monthly recommended)
- When agents keep making the same mistake despite rules existing (symptom of stale or contradictory config)
- After a major refactor where file paths, package names, or architecture changed

## When NOT to Use

- For application defects, recommend `debug`; for refactoring, recommend `/refactor`.
- If capturing a single new rule from conversation → use **rules-capture**
- If auditing code quality rather than agent configuration → use `audit`
- If setting up or repairing formatter/linter config → use `linter-formatter-init`
- If scaffolding `.agents/` from scratch → use **agent-folder-init**

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Workspace root | Yes | Path to the workspace containing repos (auto-detected from cwd) |
| Scope | No | `full` (all checks) or specific: `dedup`, `stale`, `instructions`, `cursor`, `settings` |
| Fix mode | No | `report` (default, read-only) or `fix` (apply recommended changes) |

## Workflow

### Step 1: Inventory — Discover All Config Files

Scan the workspace for every agent config file:

```bash
# Find all agent config files across workspace (including sub-repos)
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
| Layer           | Files Found | Total Lines |
|-----------------|-------------|-------------|
| CLAUDE.md       | N           | N           |
| AGENTS.override.md | N        | N           |
| AGENTS.md       | N           | N           |
| Configured fallbacks | N      | N           |
| .cursorrules    | N           | N           |
| .claude/ config | N           | N           |
| .agents/memory/ | N           | N           |
```

### Step 2: Dedup Check — Find Duplicated Rules

These rules commonly appear in multiple places. Search for each across ALL config files:

**Rules to check:**

- `any` types / `No any` — should be in AGENTS.md + hooks only
- `console.log` / logger — should be in AGENTS.md only
- Conventional commits — should be in AGENTS.md only
- AbortController — should be in AGENTS.md or a linked `.agents/memory/` topic only
- Session file naming — should be in hooks.json + one doc reference only
- Import order — should be in AGENTS.md or `.agents/memory/coding-standards.md` only
- Soft delete (`isDeleted`) — should be in `.agents/memory/data-guardrails.md` only
- Multi-tenancy (`organization: orgId`) — should be in `.agents/memory/security.md` only

For each rule, count occurrences:

```
grep "No \`any\`\|NO \`any\`\|no any types" across all config files
```

**Healthy target**: Each rule appears in max 2 files (one "teach" doc + one runtime enforcement like hooks).

**Flag**: Any rule appearing 3+ times across config files.

### Step 3: Staleness Check — Find Outdated Files

Check for stale dates and paths:

```bash
# Find files with old "Last Updated" dates (> 90 days old)
grep -r "Last Updated:" across .cursorrules, .cursor/rules

# Find hardcoded workspace paths that should be relative
grep -r "/Users/" across .agents/ config files

# Find references to directories that no longer exist
# Compare referenced paths against actual directory listing
```

**Flag**: Any file with "Last Updated" > 90 days behind current date.
**Flag**: Any hardcoded absolute path in config files.
**Flag**: Any reference to a directory that doesn't exist.

### Step 4: Codex Instruction Resolution Check

For each workspace, check the instruction chain Codex actually resolves:

- [ ] Each directory resolves at most one nonempty instruction file in this order: `AGENTS.override.md`, `AGENTS.md`, then configured fallback filenames
- [ ] The instruction chain is read from the project root down to the working directory
- [ ] `AGENTS.override.md` is used only where a subtree intentionally replaces the same-directory `AGENTS.md`
- [ ] `AGENTS.md` contains repo-specific rules and entry points
- [ ] Any fallback filenames are explicitly declared in the effective `.codex/config.toml`
- [ ] Runtime approval, sandbox, and network policy lives in the effective `.codex/config.toml` or hooks, not in assumed prose
- [ ] No `.codex/instructions.md` file or `.codex/commands` directory is presented
  as a supported Codex entry surface

Read the effective Codex configuration and record
`project_doc_fallback_filenames` plus any runtime policy before judging the
instruction chain.

**Flag**: Undocumented fallback files, accidental overrides, instruction files that
contradict runtime configuration, or unsupported `.codex/instructions.md` and `.codex/commands`
surfaces.

### Step 5: AGENTS.md Consistency Check

For each AGENTS.md:

- [ ] Has repo-specific context (not just generic "docs in .agents/")
- [ ] Links to correct `.agents/` paths that actually exist
- [ ] Consistent structure across repos

**Flag**: Any AGENTS.md that's a pure generic stub (< 20 lines with no repo-specific content).

### Step 6: Cursor Config Check

For `.cursorrules` and `.cursor/rules`:

- [ ] No emoji in headers (wastes tokens)
- [ ] "Last Updated" within 90 days
- [ ] Project paths reference actual directories
- [ ] No duplicated session file rules (hooks.json handles this)

### Step 7: Settings Audit

For `.claude/settings.json` and `.claude/settings.local.json`:

- [ ] Denied skills have documented rationale (in SETTINGS-NOTES.md or equivalent)
- [ ] Local bash overrides don't contradict documented standards without explanation
- [ ] No stale tool references

### Step 8: Generate Report

Output format:

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

### Step 9: Apply Fixes (if fix mode)

Never infer fix mode from the audit findings or from a request to "sync" configs.
Enter fix mode only when the user explicitly requests mutation, show the exact files
and operations, and obtain confirmation before using write/edit or mutating shell
behavior. Then apply changes following these principles:

- Each rule lives in ONE canonical location
- Hooks enforce at runtime — docs teach, not repeat
- Strip emoji from all config files
- Update all "Last Updated" dates
- Replace hardcoded paths with relative references
- Consolidate project instructions into AGENTS.md and scoped AGENTS.override.md files
- Move runtime approval, sandbox, and network policy into the effective `.codex/config.toml` or hooks

## Reference Files

- `references/canonical-ownership.md` — Which rule belongs in which file
- `references/healthy-config-example.md` — Example of a well-structured config set

## Anti-Patterns

| DON'T | DO | Why |
|-------|-----|-----|
| Repeat the same rule in AGENTS.md, CLAUDE.md, `.agents/memory/`, and hooks | Put the rule in ONE canonical file; others reference it | Duplication wastes context tokens and creates drift when one copy gets updated but others don't |
| Leave "Last Updated: 2025-10-07" in a file touched in 2026 | Update dates when modifying any config file | Stale dates signal neglect and erode trust in the config system |
| Create an extra instruction filename without configuring it | Put shared project guidance in AGENTS.md; use AGENTS.override.md for scoped overrides and configure any genuine fallback in the effective `.codex/config.toml` | Codex resolves native instruction names plus explicitly configured fallbacks |
| Use emoji in config headers | Use plain text headers | Emoji waste tokens on every context load and violate "no emoji unless requested" |
| Hardcode `/Users/username/path/` in config files | Use relative paths or describe location generically | Hardcoded paths break when workspace moves or another developer joins |
| Recreate a parallel legacy instruction tree under `.agents/` | Put durable guardrails in topic files under `.agents/memory/`; put shared actionable rules in AGENTS.md | The current memory layout keeps durable context discoverable without parallel hierarchies |

## Validation

After running the audit:

- [ ] No rule appears in more than 2 config files
- [ ] All `.cursorrules` files have "Last Updated" within 90 days
- [ ] Every Codex instruction file is native (`AGENTS.override.md` or `AGENTS.md`) or an explicitly configured fallback
- [ ] Runtime approval, sandbox, and network claims match the effective `.codex/config.toml` or hooks
- [ ] No hardcoded absolute paths in any config file
- [ ] No emoji in `.cursorrules` or `.cursor/rules` headers
- [ ] Denied skills in settings.json have documented rationale
- [ ] Total config file line count decreased or stayed flat (no bloat)

## Related Skills

- `rules-capture` — capture one new preference instead of auditing a config set
- `agent-folder-init` — scaffold a missing `.agents/` structure
- `linter-formatter-init` — set up or repair formatter/linter configuration
- `audit` — audit application quality instead of agent configuration
