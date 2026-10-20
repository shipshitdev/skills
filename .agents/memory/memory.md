# Skills Repo Memory

last_verified: 2026-10-20

## What This Repo Is

Public skills library at `shipshitdev/skills`: 25 user-invoked skills, installed
with `bunx skills add shipshitdev/skills --skill <name>`. Works with Claude Code,
Codex, and Cursor. No marketplace bundles, commands, or generated catalog.

## Repo Identity

- **Name:** ship-shit-dev-library
- **Owner:** shipshitdev — solo maintainer, zero-code workflow
- **License:** MIT
- **Runtime:** Bun (never npm/yarn/pnpm)
- **Linting:** markdownlint (markdown), biome (JSON), shellcheck (bash)
- **CI:** `checks` on every PR — lint, validate, test, `bun audit`

## Architecture Decisions

### User-invoked only, trimmed to 28 (2026-10-20)

Vincent wants these skills used only when he runs them. Every skill sets
`disable-model-invocation: true`; `user-invocable: false` is forbidden because it
would make a skill unreachable. The validator enforces both. The library was cut
from 132 skills to the 28 he runs; `commands/`, `bundles/`, `catalog.json`,
`.claude-plugin/`, `docs/`, `prompts/`, plugin manifests, per-skill versions and
the generation scripts were removed. Slash names now equal skill names.

Because the Skill tool cannot load user-only skills, a composing skill runs a
delegate by reading its installed playbook (`<router>/references/<action>.md` for
`/<router> <action>`, `<name>/SKILL.md` for `/<name>`) and following it. Handoffs
the user should start stay as `Recommend /<command>`.

### Upstream pstack and Pocock skills (2026-10-19, amended 2026-10-20)

pstack (Claude Code plugin `pstack@cursor-plugins` from `cursor/plugins`) and
`mattpocock/skills` are maintained upstream, so this repo does not vendor or
rewrite them. Skills here name them as "upstream pstack/mattpocock when
installed", never as relative routes.

### Single-Source Skills (2026-02-04)

One `skills/` directory at root. No per-platform copies. Platform-neutral
writing: no tool names, imperative style.

### Agent Skills Spec Compliance (2026-04-21)

Follow agentskills.io/specification as base, with Claude Code extensions on top.
`tags` and provenance go inside `metadata:` as strings. See
`.agents/memory/system/skill-standards.md`.

### Single release version (2026-10-03, amended 2026-10-20)

Skills carry no version. release-please bumps `package.json`, the only version.

### Session Logs Are Local-Only (2026-06-19)

`.agents/sessions/` is gitignored — session logs stay local in this public repo.
Do not `git add -f` them. Durable decisions go in `.agents/memory/*.md`.

### EARS Acceptance Criteria (2026-06-19)

PRD/spec skills standardize acceptance criteria on EARS:
`WHEN/WHILE/WHERE/IF … THE SYSTEM SHALL …`, or a bare `THE SYSTEM SHALL …`.
`/issue check` validates each Acceptance Criteria bullet against
`^\s*(\d+\.\s*)?(WHEN|WHILE|WHERE|IF|THE SYSTEM)\b.*\bSHALL\b`; execution
readiness is blocking. Applies to `/issue prd`, `/issue check`,
`/issue feature`, and `/issue publish`.

### Prepared issue delivery (2026-09-14)

One end-to-end feature per issue/PR by default. `/issue feature` composes the PRD,
plan, readiness gate, and task-creation skills.
`issue/references/execution-readiness.md` owns preparation readiness;
`execute/references/delivery-gate.md` owns delivery readiness. Executors
implement settled decisions and escalate gaps. Harnesses own model, effort, and
capacity configuration.

### Project session coordination (2026-10-07)

`orchestrate` is the user-invoked project-session coordinator: it enrolls existing
project chats, keeps one decision queue, and relays answers. New sessions need a
human request.

### Weekly review composition (2026-09-05, amended 2026-10-20)

`/check week` coordinates board evidence, issue-to-code checks, operational
evidence, and the repo's dependency audit. Report-only is the default; board
writes and deployment actions keep their own boundaries.

## Known Issues

- Codex has no equivalent of `disable-model-invocation` in these skills yet, so
  Codex may still select them implicitly.

## Key Files

- `.agents/memory/system/skill-standards.md` — authoritative spec
- `.agents/memory/system/execution-boundary.md` — harness versus skill ownership
- `scripts/validate.py` — skill validator (`bun run validate`)
- `scripts/tests/test_validate.py` — validator tests
