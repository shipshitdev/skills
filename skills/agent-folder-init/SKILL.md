---
name: agent-folder-init
description: "Adds or repairs .agents/ project context in an existing repo: docs, session tracking, tasks, coding standards. Not for scaffolding a new product."
metadata:
  version: "2.2.2"
  tags: "agents, setup, documentation"
---

# Agent Folder Init

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- Existing project root
- Project name and primary tech stack
- Optional platform entry surfaces: Claude Code, Codex, and/or Cursor

Outputs:

- Dry-run plan by default
- `.agents/` documentation structure and root `AGENTS.md` after explicit `--write`
- Optional `CLAUDE.md` or `.cursor/rules/agent-context.mdc` only when that
  platform is explicitly selected; Codex uses `AGENTS.md`
- Summary of planned, written, skipped, and unchanged files

Creates/Modifies:

- `.agents/`, root `AGENTS.md`, optional `CLAUDE.md`, optional Cursor project rule,
  and `.editorconfig`
- Does not create application source code

External Side Effects:

- None in the default dry run; `--write` performs local file writes only

Confirmation Required:

- Before any write: review the dry-run plan and explicitly rerun with `--write`
- Before overwriting an existing entry file: add `--force-entry-files`; symlink and
  non-file targets are always refused
- Before writing outside the current workspace

Delegates To:

- `project-init-orchestrator` when starting a new product repo
- `fullstack-workspace-init` / `npx @shipshitdev/v0` when a new Shipshit.dev product should be scaffolded
- `agent-config-audit` after generation to detect drift or stale config

## Purpose

This skill plans, then scaffolds a lean AI agent documentation system including:

- Session tracking (daily files in `.agents/sessions/`)
- Durable project context in `.agents/memory/` (one topic per file)
- Supported platform entry surfaces without copying commands, rules, agents, user
  settings, or another project's configuration

## When to Use

- Adding AI coding-assistant context to an existing project
- Setting up AI-first development workflows
- Migrating an existing project to use structured AI documentation

For new Shipshit.dev product repos, prefer `project-init-orchestrator`, which
routes to `npx @shipshitdev/v0` and includes the standard `.agents`, `.claude`,
and `.codex` setup.

## Usage

Run the scaffold script:

```bash
python3 scripts/scaffold.py --help

# Basic usage
python3 scripts/scaffold.py \
  --root /path/to/project \
  --name "My Project"

# Review the plan, then write the shared files
python3 scripts/scaffold.py \
  --root /path/to/project \
  --name "My Project" \
  --write \
  --allow-outside

# Add only the documented Claude and Cursor entry surfaces
python3 scripts/scaffold.py \
  --root /path/to/project \
  --name "My Project" \
  --platform claude \
  --platform cursor \
  --write \
  --allow-outside
```

The default is always a dry run. `--force-entry-files` is the only flag that permits
overwriting `AGENTS.md`, `CLAUDE.md`, or the generated Cursor entry rule. Other
existing files are preserved.

## Generated Structure

### Documentation (.agents/)

```
.agents/
├── README.md                    # Navigation hub
├── memory/
│   └── README.md                # Source of truth for durable project facts
└── sessions/
    ├── README.md                # Session format guide
    └── TEMPLATE.md              # Session file template
```

**Shared rules and coding standards** go in the applicable `AGENTS.md`. Use
`AGENTS.override.md` only for an intentional subtree override and `CLAUDE.md`
only for Claude-specific additions. Durable supporting detail belongs in
`.agents/memory/`.

**Task tracking** uses GitHub Issues (`gh issue list`, `gh issue create`) — not local task files.

### Platform entry surfaces

```
AGENTS.md                         # shared instructions; native Codex entry
CLAUDE.md                         # only with --platform claude
.cursor/rules/agent-context.mdc   # only with --platform cursor
```

The scaffold never generates `.codex/commands`, copies user settings, or imports a
library checkout. It copies only four `.agents/` templates, `.editorconfig`, and the
explicitly selected entry templates. Missing canonical assets are a hard failure before
any write; there is no embedded or stale fallback.

### Root Files

- `AGENTS.md` - Shared project instructions and `.agents/` navigation
- `CLAUDE.md` - Optional Claude-specific additions that reference `AGENTS.md`
- `.editorconfig` - Editor configuration

## Key Patterns

### memory/ Files

- One topic per file: `memory/architecture.md`, `memory/deployment.md`, `memory/entities.md`, etc.
- Every file carries a `last_verified: YYYY-MM-DD` front-matter field.
- Transient or short-lived facts add `status: temporary`.

### Session Files

- **One file per day**: `sessions/YYYY-MM-DD.md`
- Multiple sessions same day use Session 1, Session 2, etc. in the same file.

## Customization

After scaffolding, customize:

1. Root agent entry file - Add project-specific coding standards and "never do" rules
2. `.agents/memory/architecture.md` - Document your architecture decisions
3. `.agents/memory/entities.md` - Document your data entities
4. `.agents/memory/deployment.md` - Document deployment steps and gotchas
5. GitHub Issues - Create issues for tasks (`gh issue create`)
6. Platform entry files - Add only harness-specific guidance that cannot live in
   shared `AGENTS.md`

## Integration with Other Skills

This skill integrates with:

| Skill | How It Works Together |
|-------|----------------------|
| `project-init-orchestrator` | Routes new product requests to v0 before lower-level setup |
| `fullstack-workspace-init` | Uses v0 for new Shipshit.dev product workspaces |
| `linter-formatter-init` | Sets up quality tooling in the scaffolded project |
| `husky-test-coverage` | Enforces test coverage in pre-commit hooks |
