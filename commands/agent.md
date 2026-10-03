---
description: "Agent architecture, config, and setup: audit an agent system, sync agent configs, scaffold .agents/, or wire routing."
argument-hint: "[audit|config|init|route]"
disable-model-invocation: true
---

# Agent - One Front Door for Agent Architecture, Config, and Setup

Drive agent/subagent architecture, configuration, and setup from one command —
audit an agent system for failures, check config drift across workspaces, scaffold
the `.agents/` folder, or wire up dev-loop routing.

## Usage

```bash
/agent              # status: one-line domain summary + usage
/agent audit        # diagnose LLM wrapper regressions, prompt/memory contamination, tool discipline failures
/agent config       # audit and sync AGENTS.md, overrides, fallbacks, CLAUDE.md, hooks, and settings
/agent init         # scaffold or repair the .agents/ folder and root agent entry files for a repo
/agent route        # write the ## Agent skills routing block in CLAUDE.md/AGENTS.md + docs/agents/
```

`/agent help` prints this Usage block and stops without running anything.

## Steps

- **`audit`** — the `agent-architecture-audit` skill: diagnose failures in LLM and
  agent applications by inspecting wrapper regressions, prompt or memory
  contamination, tool discipline failures, hidden repair loops, and output
  rendering corruption. Produces a severity-ranked findings report and an ordered
  fix plan.
- **`config`** — the `agent-config-audit` skill: audit and sync AI agent
  instruction files (AGENTS.override.md, AGENTS.md, configured fallbacks,
  CLAUDE.md, .cursorrules, hooks, and settings) across workspaces. Use when agent
  configs drift, rules duplicate, files go stale, or after workspace restructuring.
- **`init`** — the `agent-folder-init` skill: add or repair the `.agents/` project
  context for an existing repo. Creates the `.agents/` folder structure plus root
  shared AGENTS.md and optional Claude-specific CLAUDE.md without touching
  application source code.
- **`route`** — the `setup-agent-routing` skill: write a machine-readable
  `## Agent skills` routing block in CLAUDE.md/AGENTS.md and seed `docs/agents/`
  reference files so the dev-loop skills (executing-plans, feature-intake,
  prd-writer, qa-reviewer) know this repo's GitHub issue tracker, kanban label
  vocabulary, and domain doc layout.

## Workflow

Use the `agent-dispatch` skill. It parses the subcommand and delegates to the
right engine. Read-only until the delegated skill's own confirmation gate; it
never writes files or mutates config directly.

1. **Parse the argument** into a mode (`status` / `audit` / `config` / `init` /
   `route`). Unknown argument → print Usage, do not guess.
2. **Route** to the delegated skill (or, for `status`, print a one-line domain
   summary and stop).
3. **Defer** preconditions and confirmation to the delegated skill — this command
   does not relax them.
