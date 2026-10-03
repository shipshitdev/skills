---
name: agent-dispatch
description: >-
  Single front door for agent/subagent architecture, config, and setup. Parses a
  subcommand — audit, config, init, or route — and routes to the right engine:
  agent-architecture-audit (diagnose LLM wrapper and agent failures),
  agent-config-audit (audit and sync AI agent config files across workspaces),
  agent-folder-init (add or repair .agents/ project context for a repo), or
  setup-agent-routing (write a machine-readable routing block in CLAUDE.md/AGENTS.md).
  Backs the /agent command. Use when asked to audit an agent system, check config
  drift, initialize agent docs, or wire up routing, and the action must be picked
  from an argument like "audit", "config", "init", or "route".
metadata:
  version: "2.2.2"
  tags: "agents, dispatcher, architecture, config, setup, routing, orchestration"
  author: Ship Shit Dev
when_to_use: "/agent, agent audit, config audit, init agent folder, setup agent routing, audit LLM wrappers, check agent config drift, add .agents/ folder, wire up dev-loop routing"
disable-model-invocation: true
---

# Agent Dispatch

The router behind `/agent`. Turns a subcommand into the right action and delegates. Contains no logic of its own — delegates to `agent-architecture-audit`, `agent-config-audit`, `agent-folder-init`, and `setup-agent-routing`.

## Composition Boundary

Run only the selected mode. Pass the user's target, authorized actions, and
report-only restrictions to the engine. Existing explicit approval satisfies
that engine's gate for the same scope; obtain approval for missing or expanded
authority. Delegation never grants new host, provider, cost, publication, or
production permissions. An empty or advisory mode starts no mutating workflow.

## Contract

Inputs:

- A single argument string (may be empty) parsed into a `mode`.

Outputs:

- For `audit`: a severity-ranked findings report diagnosing LLM wrapper and agent
  failures, with a layer-by-layer fix plan.
- For `config`: an audit report covering AGENTS.override.md, AGENTS.md,
  configured fallbacks, CLAUDE.md, .cursorrules, hooks, and settings, with
  proposed fixes.
- For `init`: a scaffolded `.agents/` folder structure plus root agent entry
  files, with a summary of files created versus skipped.
- For `route`: a drafted `## Agent skills` routing block in CLAUDE.md/AGENTS.md
  and seeded `docs/agents/` reference files.
- For _(empty)_: a one-line domain status summary and the Usage block.

Creates/Modifies:

- Nothing directly. The delegated skill performs any mutation behind its own
  confirmation gate.

External Side Effects:

- None by default. The delegated skills may read git remotes, `gh` APIs, or
  workspace files when resolving routing state.

Confirmation Required:

- This skill is explicit-invoke only (`disable-model-invocation`). Each delegated
  skill owns its own confirmation gate before writing files or changing config.
  This router does not relax them.

Delegates To:

- `agent-architecture-audit` for `audit` (diagnose LLM and agent wrapper failures).
- `agent-config-audit` for `config` (audit and sync agent config files).
- `agent-folder-init` for `init` (scaffold or repair the `.agents/` folder).
- `setup-agent-routing` for `route` (write the dev-loop routing block).

## Step 1 — Parse the Subcommand

Resolve the raw argument into a `mode`.

| Argument | Mode | Delegates to |
|---|---|---|
| _(empty)_ | `status` | none — print a one-line domain summary + Usage block |
| `audit` | `audit` | `agent-architecture-audit` |
| `config` | `config` | `agent-config-audit` |
| `init` | `init` | `agent-folder-init` |
| `route` | `route` | `setup-agent-routing` |

If the argument matches none of these, report the unrecognized input and print
the Usage block — do not guess a mode.

## Step 2 — Route

- **status →** print a one-line summary of the agent domain (no mutation), then
  show the Usage block.
- **audit →** apply the `agent-architecture-audit` skill.
- **config →** apply the `agent-config-audit` skill.
- **init →** apply the `agent-folder-init` skill.
- **route →** apply the `setup-agent-routing` skill.

## Usage

```bash
/agent              # status: one-line domain summary + usage
/agent audit        # diagnose LLM wrapper regressions, prompt/memory contamination, tool discipline failures
/agent config       # audit and sync AGENTS.md, overrides, fallbacks, CLAUDE.md, hooks, and settings
/agent init         # scaffold or repair the .agents/ folder and root agent entry files for a repo
/agent route        # write the ## Agent skills routing block in CLAUDE.md/AGENTS.md + docs/agents/
```

## Anti-Patterns

- **Re-implementing logic here.** All domain logic belongs in the routed skill.
- **Guessing on an unknown argument.** Print Usage instead — a wrong guess could overwrite config or scaffold into the wrong directory.
- **Skipping the delegated skill's confirmation gate.** Each routed skill controls its own writes.
- **Auto-running a mutating sub-skill on an empty argument.** The default mode prints status only; it never initiates a write.
