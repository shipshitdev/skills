---
name: agent-folder-init
description: "Adds or repairs .agents/ project context in an existing repo: docs, session tracking, tasks, coding standards. Not for scaffolding a new product."
metadata:
  version: "2.2.4"
  tags: "agents, setup, documentation"
---

# Agent Folder Init

Plans, then scaffolds, a lean AI agent documentation system in an existing project. It does not create application source code.

## Scope and guardrails

- Act only within the user's request; ask before expanding scope.
- The default is always a dry run. Review the plan, then rerun with `--write` to perform local file writes.
- `--force-entry-files` is the only flag that permits overwriting `AGENTS.md`, `CLAUDE.md`, or the generated Cursor entry rule. Other existing files are preserved. Symlink and non-file targets are always refused.
- Writing outside the current workspace requires `--allow-outside` and the user's confirmation.
- Missing canonical assets are a hard failure before any write; there is no embedded or stale fallback.

## Inputs

- Existing project root
- Project name and primary tech stack
- Optional platform entry surfaces: Claude Code, Codex, and/or Cursor (Codex uses `AGENTS.md`)

## When to use

- Adding AI coding-assistant context to an existing project
- Setting up AI-first development workflows
- Migrating a project to structured AI documentation

For a brand-new product repo, use a project-initialization workflow instead. To detect drift or stale config after generation, run an agent-config audit.

## Usage

Run the scaffold script (requires `python3`):

```bash
python3 scripts/scaffold.py --help

# Basic usage (dry run)
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

Report planned, written, skipped, and unchanged files afterwards.

## Generated structure

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

Shared rules and coding standards go in the applicable `AGENTS.md`. Use `AGENTS.override.md` only for an intentional subtree override and `CLAUDE.md` only for Claude-specific additions. Durable supporting detail belongs in `.agents/memory/`.

Task tracking uses GitHub Issues (`gh issue list`, `gh issue create`), not local task files.

### Platform entry surfaces

```
AGENTS.md                         # shared instructions; native Codex entry
CLAUDE.md                         # only with --platform claude
.cursor/rules/agent-context.mdc   # only with --platform cursor
```

The scaffold never generates `.codex/commands`, copies user settings, or imports a library checkout. It copies only four `.agents/` templates, `.editorconfig`, and the explicitly selected entry templates.

### Root files

- `AGENTS.md`: shared project instructions and `.agents/` navigation
- `CLAUDE.md`: optional Claude-specific additions that reference `AGENTS.md`
- `.editorconfig`: editor configuration

## Key patterns

### memory/ files

- One topic per file: `memory/architecture.md`, `memory/deployment.md`, `memory/entities.md`, etc.
- Every file carries a `last_verified: YYYY-MM-DD` front-matter field.
- Transient or short-lived facts add `status: temporary`.

### Session files

- One file per day: `sessions/YYYY-MM-DD.md`.
- Multiple sessions on the same day use Session 1, Session 2, etc. in the same file.

## Customize after scaffolding

1. Root agent entry file: add project-specific coding standards and "never do" rules.
2. `.agents/memory/architecture.md`: document architecture decisions.
3. `.agents/memory/entities.md`: document data entities.
4. `.agents/memory/deployment.md`: document deployment steps and gotchas.
5. GitHub Issues: create issues for tasks (`gh issue create`).
6. Platform entry files: add only harness-specific guidance that cannot live in shared `AGENTS.md`.

## Related

Linter/formatter setup and pre-commit test-coverage enforcement are separate concerns; set them up in the scaffolded project with their own skills if available.

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
- `project-init-orchestrator` (v0 route) / `npx @shipshitdev/v0` when a new Shipshit.dev product should be scaffolded
- `agent-config-audit` after generation to detect drift or stale config
