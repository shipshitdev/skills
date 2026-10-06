# Catalog naming inventory

Migration from the catalog after board correctness and composition repairs,
2026-09-05, kept current through the 2026-10-06 consolidation (#235). This is
a migration inventory, not a runtime registry.

169 skills and 24 commands. Eight rows record a rename from an earlier name (one of
them, `gh-address-comments`, was later merged into `pr-comments`). Skills folded into
another since the migration are listed under Retired skills. Owning surfaces describe
contracts; they are not mandatory naming prefixes.

## Skills

| Current | Canonical | Action | Owning surface |
|---|---|---|---|
| `accessibility` | `accessibility` | retain | accessibility |
| `agent-architecture-audit` | `agent-architecture-audit` | retain | agent-architecture |
| `agent-config-audit` | `agent-config-audit` | retain | agent-configuration |
| `agent-dispatch` | `agent-dispatch` | retain | agent-configuration |
| `agent-folder-init` | `agent-folder-init` | retain | agent-configuration |
| `ai-agent-cost-optimizer` | `ai-agent-cost-optimizer` | retain | agent-cost |
| `ai-loading-ux` | `ai-loading-ux` | retain | design |
| `api-design-expert` | `api-design-expert` | retain | api-design |
| `architect` | `architect` | retain | architecture |
| `arena` | `arena` | retain | agent-orchestration |
| `artifacts-builder` | `artifacts-builder` | retain | artifact-production |
| `ask-dev-loop` | `ask-dev-loop` | retain | workflow-navigation |
| `audit` | `audit` | retain | design |
| `aws-infrastructure` | `aws-infrastructure` | retain | aws-infrastructure |
| `blast-radius` | `blast-radius` | retain | change-analysis |
| `bug` | `bug` | retain | issue-intake |
| `clarify` | `clarify` | retain | design |
| `code-review` | `code-review` | retain | code-review |
| `codebase-design` | `codebase-design` | retain | architecture |
| `codex-image-gen` | `codex-image-gen` | retain | artifact-production |
| `comment-mode` | `comment-mode` | retain | document-feedback |
| `commit-summary` | `commit-summary` | retain | git |
| `component-library` | `component-library` | retain | react-components |
| `content-script-developer` | `content-script-developer` | retain | browser-extensions |
| `context-optimization` | `context-optimization` | retain | agent-context |
| `create-verification-skill` | `create-verification-skill` | retain | skill-maintenance |
| `critique` | `critique` | retain | design |
| `cto-advisor` | `cto-advisor` | retain | engineering-leadership |
| `debug` | `debug` | retain | debugging |
| `dependency-audit` | `dependency-audit` | retain | dependency-security |
| `deploy` | `deploy-app` | rename | deployment |
| `deploy-dispatch` | `deploy-dispatch` | retain | deployment |
| `deployment-composer` | `deployment-composer` | retain | deployment |
| `design-consistency-auditor` | `design-consistency-auditor` | retain | design |
| `design-dispatch` | `design-dispatch` | retain | design |
| `deslop` | `deslop` | retain | code-cleanup |
| `devcontainer-setup` | `devcontainer-setup` | retain | development-environment |
| `docker-expert` | `docker-expert` | retain | containers |
| `docs` | `docs` | retain | documentation |
| `domain-modeling` | `domain-modeling` | retain | architecture |
| `ec2-backend-deployer` | `ec2-backend-deployer` | retain | aws-infrastructure |
| `env-setup` | `env-setup` | retain | development-environment |
| `error-handling-expert` | `error-handling-expert` | retain | error-handling |
| `evaluation` | `evaluation` | retain | agent-evaluation |
| `executing-plans` | `executing-plans` | retain | agent-orchestration |
| `expo-architect` | `expo-architect` | retain | expo-mobile |
| `feature-intake` | `feature-intake` | retain | issue-intake |
| `figure-it-out` | `figure-it-out` | retain | agent-orchestration |
| `finishing-a-development-branch` | `finishing-a-development-branch` | retain | git |
| `fix-merge-conflicts` | `fix-merge-conflicts` | retain | git |
| `frontend-design` | `frontend-design` | retain | design |
| `full-code-review` | `full-code-review` | retain | code-review |
| `gh-address-comments` | `pr-comments` | rename, then merged (#190) | pull-request-feedback |
| `gh-board-sync` | `board-sync` | rename | board-workflow |
| `gh-fix-ci` | `github-fix-ci` | rename | github |
| `gh-inbox` | `github-inbox` | rename | github |
| `gh-pr-publish` | `github-pr-publish` | rename | github |
| `gh-project-board` | `project-board` | rename | board-workflow |
| `gh-review-suggestions` | `github-review-suggestions` | rename | github |
| `git-cleanup` | `git-cleanup` | retain | git |
| `git-safety` | `git-safety` | retain | git |
| `github-actions-author` | `github-actions-author` | retain | github |
| `graphql-architect` | `graphql-architect` | retain | api-design |
| `grill-me` | `grill-me` | retain | discovery |
| `grok-review` | `grok-review` | retain | grok-review |
| `handoff` | `handoff` | retain | agent-context |
| `how` | `how` | retain | code-explanation |
| `html-style` | `html-style` | retain | design |
| `husky-test-coverage` | `husky-test-coverage` | retain | code-quality-tooling |
| `icp` | `icp` | retain | product-strategy |
| `incremental-fetch` | `incremental-fetch` | retain | data-ingestion |
| `interrogate` | `interrogate` | retain | code-review |
| `interview` | `interview` | retain | discovery |
| `landing-page-vercel` | `landing-page-vercel` | retain | landing-pages |
| `layout` | `layout` | retain | design |
| `linter-formatter-init` | `linter-formatter-init` | retain | code-quality-tooling |
| `llm-structured-output` | `llm-structured-output` | retain | llm-output |
| `maintain-verification-skill` | `maintain-verification-skill` | retain | skill-maintenance |
| `mcp-builder` | `mcp-builder` | retain | mcp |
| `memory-systems` | `memory-systems` | retain | agent-context |
| `merge-open-prs` | `merge-open-prs` | retain | pull-request-integration |
| `micro-landing-builder` | `micro-landing-builder` | retain | landing-pages |
| `monitoring-setup` | `monitoring-setup` | retain | observability |
| `multi-agent-patterns` | `multi-agent-patterns` | retain | agent-architecture |
| `nestjs-expert` | `nestjs-expert` | retain | nestjs |
| `nestjs-queue-architect` | `nestjs-queue-architect` | retain | nestjs |
| `nestjs-testing-expert` | `nestjs-testing-expert` | retain | nestjs |
| `nextra-writer` | `nextra-writer` | retain | documentation |
| `no-comments` | `no-comments` | retain | code-cleanup |
| `open-source-checker` | `open-source-checker` | retain | open-source-release |
| `package-architect` | `package-architect` | retain | package-design |
| `performance-expert` | `performance-expert` | retain | performance |
| `playwright-e2e-init` | `playwright-e2e-init` | retain | e2e-testing |
| `polish` | `polish` | retain | design |
| `postgres-ops` | `postgres-ops` | retain | postgres-operations |
| `pr-comments` | `pr-comments` | retain | pull-request-feedback |
| `prd-dispatch` | `prd-dispatch` | retain | product-specification |
| `prd-quality-gate` | `prd-quality-gate` | retain | product-specification |
| `prd-task-creator` | `prd-task-creator` | retain | product-specification |
| `prd-writer` | `prd-writer` | retain | product-specification |
| `production-audit` | `production-audit` | retain | production-readiness |
| `project-init-orchestrator` | `project-init-orchestrator` | retain | product-initialization |
| `prompt-engineering` | `prompt-engineering` | retain | prompt-design |
| `prototype` | `prototype` | retain | prototyping |
| `pstack` | `pstack` | retain | agent-orchestration |
| `qa-loop` | `qa-loop` | retain | qa |
| `qa-reviewer` | `qa-reviewer` | retain | qa |
| `quick-view` | `quick-view` | retain | artifact-production |
| `quieter` | `quieter` | retain | design |
| `react-component-performance` | `react-component-performance` | retain | react |
| `react-hook-form` | `react-hook-form` | retain | react |
| `react-native-components` | `react-native-components` | retain | react-components |
| `react-patterns` | `react-patterns` | retain | react |
| `react-refactor` | `react-refactor` | retain | react |
| `react-testing-library` | `react-testing-library` | retain | react |
| `recall` | `recall` | retain | agent-context |
| `receiving-code-review` | `receiving-code-review` | retain | code-review |
| `redis-caching` | `redis-caching` | retain | redis |
| `refactor-code` | `refactor-code` | retain | refactoring |
| `release` | `release` | retain | release |
| `research` | `research` | retain | product-research |
| `retro` | `retro` | retain | agent-memory |
| `review-dispatch` | `review-dispatch` | retain | code-review |
| `roadmap-analyzer` | `roadmap-analyzer` | retain | product-strategy |
| `roadmap-to-milestones` | `roadmap-to-milestones` | retain | roadmap-scheduling |
| `rules-capture` | `rules-capture` | retain | agent-memory |
| `scaffold` | `scaffold` | retain | code-scaffolding |
| `security-audit` | `security-audit` | retain | application-security |
| `security-expert` | `security-expert` | retain | application-security |
| `setup-agent-routing` | `setup-agent-routing` | retain | agent-configuration |
| `setup-pstack` | `setup-pstack` | retain | agent-orchestration |
| `shadcn` | `shadcn` | retain | shadcn |
| `shadcn-setup` | `shadcn-setup` | retain | shadcn |
| `shape` | `shape` | retain | design |
| `show-me-your-work` | `show-me-your-work` | retain | work-evidence |
| `skill-capture` | `skill-capture` | retain | skill-maintenance |
| `skill-comply` | `skill-comply` | retain | skill-maintenance |
| `skill-creator` | `skill-creator` | retain | skill-maintenance |
| `skill-dispatch` | `skill-dispatch` | retain | skill-maintenance |
| `skill-scout` | `skill-scout` | retain | skill-maintenance |
| `stack-modernization` | `stack-modernization` | retain | stack-modernization |
| `stack-validator` | `stack-validator` | retain | stack-configuration |
| `standup` | `standup` | retain | work-summary |
| `stripe-implementer` | `stripe-implementer` | retain | stripe |
| `structural-review` | `structural-review` | retain | code-review |
| `swarm` | `swarm` | retain | agent-orchestration |
| `table-filters` | `table-filters` | retain | design |
| `tailwind` | `tailwind` | retain | tailwind |
| `tdd` | `tdd` | retain | testing |
| `teach` | `teach` | retain | code-explanation |
| `tech-debt` | `tech-debt` | retain | refactoring |
| `technical-writing` | `technical-writing` | retain | documentation |
| `test-dispatch` | `test-dispatch` | retain | testing |
| `test-runner` | `test-runner` | retain | testing |
| `testing-cicd-init` | `testing-cicd-init` | retain | testing |
| `testing-expert` | `testing-expert` | retain | testing |
| `theme-factory` | `theme-factory` | retain | artifact-production |
| `tool-design` | `tool-design` | retain | agent-architecture |
| `turborepo` | `turborepo` | retain | monorepo |
| `typescript-expert` | `typescript-expert` | retain | typescript |
| `vercel-deploy` | `vercel-deploy` | retain | vercel |
| `verification-before-completion` | `verification-before-completion` | retain | work-evidence |
| `wait-what` | `wait-what` | retain | code-explanation |
| `wayfinder` | `wayfinder` | retain | product-specification |
| `weekly-review` | `weekly-review` | retain | engineering-maintenance |
| `why` | `why` | retain | code-explanation |
| `wizard` | `wizard` | retain | human-setup |
| `workspace-performance-audit` | `workspace-performance-audit` | retain | performance |
| `worktree` | `worktree` | retain | git |
| `writing-plans` | `writing-plans` | retain | product-specification |

## Retired skills

Folded into another skill since the migration. Use the destination instead; removed
names no longer install through `npx skills add --skill <name>`.

| Retired | Now | Change |
|---|---|---|
| `ai-regression-testing` | `testing-expert` (AI regression mode) | #169 |
| `execution-debugging` | `debug` (scoped mode) | #169 |
| `systematic-debugging` | `debug` (`references/systematic-debugging.md`) | #169 |
| `context-fundamentals` | `context-optimization` (`references/fundamentals.md`) | #169 |
| `release-dispatch` | `release` | #167 |
| `release-pr-gates` | `release` | #167 |
| `changelog-generator` | `release` (`notes` mode, `references/notes.md`) | #190 |
| `typescript-refactor` | `typescript-expert` (`references/rules/`) | #190 |
| `spec-first` | `prd-dispatch` (`spec` mode) | #190 |
| `fullstack-workspace-init` | `project-init-orchestrator` | #190 |
| `grilling` | `grill-me` (renamed back; `/grill-me` is the name in use) | rename |
| `biome-validator` | `stack-validator` (`--stack biome`, `references/biome.md`) | #190 |
| `bun-validator` | `stack-validator` (`--stack bun`, `references/bun.md`) | #190 |
| `clerk-validator` | removed: Clerk is no longer part of the house stack (Better Auth); the `clerk` stack and `references/clerk.md` were dropped from `stack-validator` | #223 |
| `nextjs-validator` | `stack-validator` (`--stack nextjs`, `references/nextjs.md`) | #190 |
| `tailwind-validator` | `stack-validator` (`--stack tailwind`, `references/tailwind.md`) | #190 |
| `refactor-dispatch` | deleted; `/refactor` routes to its engines directly | #190 |
| `context-engineering` | removed: no consumers; execution skills read repo instructions themselves | #190 |
| `mongodb-atlas-checker` | removed: the house stack is Postgres only; use `postgres-ops` | #207 |
| `mongodb-migration-expert` | removed: the house stack is Postgres only; use `postgres-ops` (Prisma migrations) | #207 |
| `advanced-evaluation` | `evaluation` (LLM-as-judge mode, `references/llm-as-judge.md`) | #235 |
| `context-degradation` | `context-optimization` (diagnose mode, `references/degradation.md`) | #235 |
| `codebase-advisor` | `codebase-design` (`survey`, `report`, `deepen` and the other survey modes, `references/survey.md`) | #235 |
| `agent-browser` | removed: it wrapped a third-party CLI that overlaps the harness's built-in browser and page-automation tools; `qa-loop` names those tools instead | #235 |

## Commands

| Current | Canonical | Action | Owning surface |
|---|---|---|---|
| `/address` | `/address` | retain | pull-request-feedback |
| `/agent` | `/agent` | retain | agent-configuration |
| `/ask` | `/ask` | retain | workflow-navigation |
| `/board` | `/board` | retain | board-workflow |
| `/cleanup` | `/cleanup` | retain | git |
| `/codex-loop` | `/codex-loop` | retain | agent-orchestration |
| `/deploy` | `/deploy` | retain | deployment |
| `/design` | `/design` | retain | design |
| `/env` | `/env` | retain | development-environment |
| `/feature` | `/feature` | retain | issue-intake |
| `/fix-ci` | `/fix-ci` | retain | ci-repair |
| `/loop` | `/loop` | retain | agent-orchestration |
| `/merge` | `/merge` | retain | pull-request-integration |
| `/pr` | `/pr` | retain | pull-request-lifecycle |
| `/prd` | `/prd` | retain | product-specification |
| `/prompt` | `/prompt` | retain | prompt-design |
| `/qa` | `/qa` | retain | qa |
| `/refactor` | `/refactor` | retain | refactoring |
| `/review` | `/review` | retain | code-review |
| `/roadmap` | `/roadmap` | retain | roadmap-planning |
| `/scan` | `/scan` | retain | application-security |
| `/skill` | `/skill` | retain | skill-maintenance |
| `/suggest` | `/suggest` | retain | pull-request-feedback |
| `/test` | `/test` | retain | testing |

No prefix sweep of Git, testing, design, release, AWS, or agent skills is proposed. Retained names do not imply provider neutrality: PR comments, merge, issue filing, and milestone planning remain explicit about their current GitHub mechanisms.

The JSON companion records per-row rationale and command identifier references. `skill-contract-evidence.json` captures descriptions and Contract blocks used to assign ownership. This is a planning artifact, not a competing runtime catalog.

Root confirmed that the command names were unchanged by the migration (29 then; the `/bug`, `/deslop`, `/release`, `/standup`, `/wait-what` and `/weekly-review` command files were dropped later because the same-named skills own those slash names). The unselected alternative was to rename the three provider-only standalone adapters /address, /fix-ci, and /suggest to their github-* skill names. It is recorded rather than silently expanding the agreed seven-skill migration.
