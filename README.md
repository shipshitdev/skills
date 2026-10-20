![Ship Shit Dev Skills](./assets/banner.svg)

# Ship Shit Dev Skills

![Project Type](https://img.shields.io/badge/Project-Skills-blue)

28 user-invoked agent skills for development workflows. Works with Claude Code,
OpenAI Codex, and Cursor.

Every skill sets `disable-model-invocation: true`. The model never picks one up on
its own; you run it by name (`/git-cleanup`, `/qa-loop`, `/computer-user`). Skills
that compose others read the sibling `SKILL.md` directly, so they still work
without exposing those skills to the model.

Skills are model-agnostic playbooks: the harness supplies the model and effort, and
no skill names a concrete model. Standards live in
[`.agents/memory/system/skill-standards.md`](.agents/memory/system/skill-standards.md).

## Skills

### Plan

| Skill | What it does |
|---|---|
| `feature-intake` | Turns a rough request into one execution-ready issue. |
| `prd-writer` | Writes repository-grounded requirements with EARS acceptance criteria. |
| `writing-plans` | Resolves implementation decisions into an exact plan on the issue. |
| `prd-quality-gate` | Blocks execution until the issue holds a complete contract. |
| `prd-task-creator` | Publishes requirements and plans as a GitHub issue (and sub-issues). |
| `bug` | Files a structured Bug issue after a preview. |

### Build and verify

| Skill | What it does |
|---|---|
| `executing-plans` | Executes a prepared issue and tracks review, CI, merge, and deploy evidence. |
| `orchestrate` | Coordinates existing project sessions and routes their questions. |
| `worktree` | Creates an isolated worktree outside the repository. |
| `test-runner` | Runs tests at the right scope and reports failures with evidence. |
| `qa-loop` | Interactive localhost QA: reproduce, fix, and verify each defect. |
| `qa-reviewer` | Verification pass over finished agent work. |
| `computer-user` | Drives the project's own Brave session over the DevTools protocol. |
| `codex-image-gen` | Generates raster images through the Codex CLI. |
| `stack-validator` | Flags outdated Biome, Bun, Next.js, and Tailwind config. |

### Review

| Skill | What it does |
|---|---|
| `code-review` | Reviews a PR or diff for correctness, security, and spec fidelity. |
| `grok-review` | Second-opinion review through the Grok CLI, with every finding verified. |

### Git and GitHub

| Skill | What it does |
|---|---|
| `github-pr-publish` | Creates and updates pull requests with safe push gates. |
| `github-fix-ci` | Diagnoses and fixes failing GitHub Actions checks. |
| `fix-merge-conflicts` | Resolves conflicts correctness-first and proves the tree builds. |
| `merge-open-prs` | Reviews and lands open pull requests. |
| `git-cleanup` | Removes only proven-merged branches and worktrees. |
| `git-safety` | Blocks staged secrets and gates destructive git commands. |

### Release and operations

| Skill | What it does |
|---|---|
| `release` | Cuts a release from a green trunk. |
| `deploy-app` | Runs staging or production deployment workflows. |
| `weekly-review` | Weekly review of board accuracy, code changes, and operational health. |

### Boards

| Skill | What it does |
|---|---|
| `project-board` | Audits and configures GitHub or Jira project boards. |
| `board-sync` | Reconciles a board with current work and delivery evidence. |

## Installation

```bash
# All skills, globally, for the agents you use
bunx skills add shipshitdev/skills -g --agent claude-code codex cursor --skill '*' -y

# One skill
bunx skills add shipshitdev/skills -g --skill git-cleanup -y
```

Always pass `--agent`; `--all` installs into every agent the CLI knows (30+).

### Companion libraries

This repository does not vendor other skill libraries. Install them from upstream
so you keep receiving their updates:

- **pstack** (Claude Code plugin from `cursor/plugins`):
  `/plugin marketplace add cursor/plugins`, then `/plugin install pstack@cursor-plugins`.
- **mattpocock/skills**: `bunx skills add mattpocock/skills -g --agent claude-code -y`.

Skills here name them only as "when installed".

## Development

```bash
bun install
bun run lint       # markdownlint, biome (JSON), shellcheck
bun run validate   # scripts/validate.py
bun run test       # validator tests and each skill's script tests
```

To add a skill, create `skills/<name>/SKILL.md` with `name` matching the
directory and `disable-model-invocation: true`, then run the three commands above.
Releases are cut by release-please from conventional commits.

## License

MIT
