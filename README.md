![Ship Shit Dev Skills](./assets/banner.svg)

# Ship Shit Dev Skills

![Project Type](https://img.shields.io/badge/Project-Skills-blue)

25 user-invoked agent skills for development workflows. Works with Claude Code,
OpenAI Codex, and Cursor.

Every skill sets `disable-model-invocation: true`. The model never picks one up on
its own; you run it by name (`/git cleanup`, `/run-qa`, `/computer-user`). Skills
that compose others read the sibling `SKILL.md` directly, so they still work
without exposing those skills to the model.

Skills are model-agnostic playbooks: the harness supplies the model and effort, and
no skill names a concrete model. Standards live in
[`.agents/memory/system/skill-standards.md`](.agents/memory/system/skill-standards.md).

## Quick start

1. Install the skills (and, optionally, the [companion libraries](#companion-libraries)):

   ```bash
   bunx skills add shipshitdev/skills -g --agent claude-code codex cursor --skill '*' -y
   ```

2. Run the core loop on a real task:

   ```text
   /file-feature add CSV export to the invoices page
   /execute-plan #123
   /review-code
   /publish-pr
   /merge-prs
   ```

Every command takes free text after its name. Bare commands with modes (`/git`,
`/orchestrate help`) print their options instead of guessing.

## How to use

### Ship a feature

```text
/file-feature <rough request>      # requirements, plan, readiness check, one issue
/execute-plan #<issue>             # implement exactly the plan, collect evidence
/run-tests                         # changed scope; `full`, `e2e`, `types`, `<path>` widen it
/review-code                       # Standards + Spec review of the branch or PR
/publish-pr                        # push and open or update the PR
/fix-ci                            # when checks go red; loops until green on request
```

Need only one piece? `/write-prd` interviews you and drafts requirements,
`/write-plan` turns settled requirements into steps, and `/check-prd` tells you
whether an issue is ready to execute. `/publish-prd` files a finished PRD as an
issue with sub-issues.

### Fix a bug

```text
/file-bug draft checkout total ignores the discount code   # preview only
/file-bug checkout total ignores the discount code         # preview, then file
/execute-plan #<bug>
```

To root-cause before filing, run an upstream debugging skill such as
`diagnosing-bugs` or `/pstack:why`.

### QA the running app

```text
/run-qa the onboarding flow on localhost      # reproduce, fix, re-verify each defect
/review-qa                                    # check finished agent work against the ask
/computer-user open the dashboard and screenshot the empty state
```

### Review

```text
/review-code                       # current branch against its base
/review-code #42                   # a PR
/review-code adversarial #42       # multi-model panel, with pstack interrogate installed
/review-with-grok #42              # second opinion from the Grok CLI, findings verified
```

### Land and clean up

```text
/merge-prs                         # review, confirm, merge green PRs, list cleanup candidates
/merge-prs review                  # review only, merge nothing
/git cleanup                       # dry-run: proves what is merged, deletes nothing
/git cleanup prune                 # remove the proven-merged branches and worktrees from that plan
/git worktree fix-auth from develop
/git conflicts                     # resolve the current merge or rebase
/git safety                        # staged-secret check before a commit
```

### Release and deploy

```text
/release                           # status of trunk, gates, and the next version
/release cut minor
/deploy staging
```

### Weekly review and retros

```text
/review-week                       # last 7 days, report only
/review-week since <SHA> --fix     # also repair confirmed findings in scope, via PRs
```

For a retrospective on how the work went (not what shipped), use the upstream
`/retro` (mattpocock) or `/pstack:reflect`.

### Run several sessions at once

```text
/orchestrate status                # what every project session is doing
/orchestrate plan bugs first       # propose lanes, dispatch nothing
/orchestrate run finish the bugs   # coordinate existing sessions, routing their questions
/orchestrate help
```

### Boards

```text
/configure-board                   # audit fields, views, and workflows on a GitHub or Jira board
/sync-board                        # reconcile cards with real PR and deploy state
```

## Skills

### Plan

| Skill | What it does |
|---|---|
| `file-feature` | Turns a rough request into one execution-ready issue. |
| `write-prd` | Writes repository-grounded requirements with EARS acceptance criteria. |
| `write-plan` | Resolves implementation decisions into an exact plan on the issue. |
| `check-prd` | Blocks execution until the issue holds a complete contract. |
| `publish-prd` | Publishes requirements and plans as a GitHub issue (and sub-issues). |
| `file-bug` | Files a structured Bug issue after a preview. |

### Build and verify

| Skill | What it does |
|---|---|
| `execute-plan` | Executes a prepared issue and tracks review, CI, merge, and deploy evidence. |
| `orchestrate` | Coordinates existing project sessions and routes their questions. |
| `run-tests` | Runs tests at the right scope and reports failures with evidence. |
| `run-qa` | Interactive localhost QA: reproduce, fix, and verify each defect. |
| `review-qa` | Verification pass over finished agent work. |
| `computer-user` | Drives the project's own Brave session over the DevTools protocol. |
| `generate-image` | Generates raster images through the Codex CLI. |
| `validate-stack` | Flags outdated Biome, Bun, Next.js, and Tailwind config. |

### Review

| Skill | What it does |
|---|---|
| `review-code` | Reviews a PR or diff for correctness, security, and spec fidelity. |
| `review-with-grok` | Second-opinion review through the Grok CLI, with every finding verified. |

### Git and GitHub

| Skill | What it does |
|---|---|
| `git` | Local git, one action per call (below). |
| `publish-pr` | Creates and updates pull requests with safe push gates. |
| `fix-ci` | Diagnoses and fixes failing GitHub Actions checks. |
| `merge-prs` | Reviews and lands open pull requests. |

`/git <action>` routes to one playbook:

| Action | What it does |
|---|---|
| `/git cleanup` | Removes only proven-merged branches and worktrees. |
| `/git safety` | Blocks staged secrets and gates destructive git commands. |
| `/git conflicts` | Resolves conflicts correctness-first and proves the tree builds. |
| `/git worktree` | Creates an isolated worktree outside the repository. |

### Release and operations

| Skill | What it does |
|---|---|
| `release` | Cuts a release from a green trunk. |
| `deploy` | Runs staging or production deployment workflows. |
| `review-week` | Weekly review of board accuracy, code changes, and operational health. |

### Boards

| Skill | What it does |
|---|---|
| `configure-board` | Audits and configures GitHub or Jira project boards. |
| `sync-board` | Reconciles a board with current work and delivery evidence. |

## Installation

```bash
# All skills, globally, for the agents you use
bunx skills add shipshitdev/skills -g --agent claude-code codex cursor --skill '*' -y

# One skill
bunx skills add shipshitdev/skills -g --skill git -y
```

Always pass `--agent`; `--all` installs into every agent the CLI knows (30+).

### Companion libraries

This repository does not vendor other skill libraries. Install them from upstream
so you keep receiving their updates:

- **pstack** (Claude Code plugin from `cursor/plugins`):
  `/plugin marketplace add cursor/plugins`, then `/plugin install pstack@cursor-plugins`.
- **mattpocock/skills**: `bunx skills add mattpocock/skills -g --agent claude-code -y`.

Skills here name them only as "when installed" and work without them. The ones
worth knowing:

| Skill | Library | Reach for it when |
|---|---|---|
| `grilling` | mattpocock | You want to be interviewed about a plan; `/write-prd` uses it when installed. |
| `interrogate` | pstack | You want a multi-model review panel; `/review-code adversarial` uses it. |
| `triage` | mattpocock | Sorting a pile of incoming issues before filing or fixing. |
| `diagnosing-bugs` | mattpocock | Root-causing a bug before `/file-bug` or a fix. |
| `why` | pstack | Tracing why code or a decision is the way it is. |
| `retro` | mattpocock | Looking back on how a stretch of work went. |
| `reflect` | pstack | Turning a session's lessons into durable rules. |
| `swarm` | pstack | Fanning one task out across parallel agents. |
| `arena` | pstack | Comparing competing implementations of the same task. |

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
