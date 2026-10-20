# Skill Standards

This repo follows the [Agent Skills open standard](https://agentskills.io/specification) as the base spec, extended with selected Claude Code-specific fields. Codex compatibility comes from the base spec plus the skill body; Claude can additionally use approved extension fields. The normative split between reusable content and app configuration lives in [Harness-Owned Execution Boundary](execution-boundary.md).

---

## Frontmatter reference

### Base spec (agentskills.io) — applies to all agents

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | **Yes** | 1–64 chars. Lowercase letters, numbers, hyphens. No leading/trailing/consecutive hyphens. No reserved words (`anthropic`, `claude`). Must match directory name. |
| `description` | **Yes** | 1–1024 chars. Written in third person. Describes what the skill does AND when to use it. Front-load key use case. |
| `license` | No | License name or reference to bundled LICENSE file. |
| `compatibility` | No | 1–500 chars. System requirements: target agent, required packages, network needs. Omit if no special requirements. |
| `metadata` | No | Map of `string → string`. Use for `tags`, `author`, provenance, and any extra data. Skills carry no version. |
| `allowed-tools` | No | Space-separated **auto-approve allowlist** — bypasses the per-use prompt for listed tools. NOT a sandbox: unlisted tools stay callable and fall through to normal permission prompts. Experimental — support varies by agent. |

### Claude Code extensions — Claude-only fields

| Field | Purpose |
|-------|---------|
| `when_to_use` | Extra trigger phrases appended to `description` in skill listing. Combined with `description`, capped at 1,536 chars. |
| `disable-model-invocation` | `true` keeps a skill user-only. Required on every skill in this repo. |
| `user-invocable` | `false` = hides from `/` menu. Forbidden here: combined with `disable-model-invocation` it makes a skill unreachable. |
| `model` | Recognized by Claude Code, but forbidden in this public library; the harness owns model selection. |
| `effort` | Recognized by Claude Code, but forbidden in this public library; the harness owns reasoning effort. |
| `context` | `fork` = run in isolated subagent. Only for skills with an actionable task — a guidelines-only skill returns **empty output** when forked. ⚠️ May not be honored via the Skill tool (issue #17283). |
| `agent` | Subagent type when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or custom. |
| `hooks` | Lifecycle hooks scoped to this skill. |
| `disallowed-tools` | Space-separated tools **removed from the pool** while the skill is active (the actual blocking mechanism; `allowed-tools` does not block). Clears on the user's next message. Use for autonomous loops that must never call a tool (e.g. `AskUserQuestion`). |
| `paths` | Glob patterns that limit when skill auto-activates. ⚠️ **Broken upstream** (issue #49835, as of v2.1.84): skills with `paths` set become undiscoverable. For monorepo scoping use nested `.claude/skills/` dirs instead. |
| `shell` | Shell for inline commands: `bash` (default) or `powershell`. |

---

## Correct frontmatter pattern

```yaml
---
name: my-skill
description: One-line summary of what it does and when to use it. Front-load the key use case — this is what Claude reads to decide whether to activate.
license: MIT
compatibility: Requires gh CLI for GitHub features.
metadata:
  tags: "tag1, tag2, tag3"
  author: Ship Shit Dev
  # For skills derived from an upstream, add source/last_synced — see Provenance.
allowed-tools: Bash(gh pr view:*) Bash(git log:*) Bash(git diff:*)
# Claude Code extensions below
when_to_use: "trigger phrase 1, trigger phrase 2, example request"
disable-model-invocation: true
---
```

---

## Common mistakes

| Wrong | Correct | Why |
|-------|---------|-----|
| `version: 1.0.0` (top-level or in `metadata`) | Remove entirely | Skills carry no version; see Versioning |
| `tags:\n  - foo\n  - bar` (top-level) | `metadata:\n  tags: "foo, bar"` | `tags` is not a spec field, and `metadata` values must be strings |
| `auto_activate: true` | Remove entirely | Not in spec, ignored by all agents |
| `auto_trigger: false` | Remove entirely | Not in spec, ignored by all agents |
| Empty `compatibility` | Omit the field | Only include if skill has real requirements |
| `description: Helps with X.` | Full sentence with trigger context | Too short, won't auto-activate reliably |

---

## Skill directory structure

```
skills/my-skill/
├── SKILL.md           # Required. Metadata + instructions. Keep under 500 lines.
├── references/        # Optional. Loaded on demand, not on activation.
│   └── full-guide.md  # Detailed docs, long examples, edge cases.
├── scripts/           # Optional. Executable code (Python, bash, Node).
└── assets/            # Optional. Templates, boilerplate, static data.
```

Keep `SKILL.md` focused: under 500 lines. Move anything detailed to `references/`.

## Scratch files

Disposable process files belong in the **current repository's** `.tmp/`
directory, not `/tmp` or `/private/tmp`.

```bash
REPO_TMP="$(git rev-parse --show-toplevel)/.tmp"
mkdir -p "$REPO_TMP"
# write "$REPO_TMP/snapshot.json", "$REPO_TMP/body.md", …
```

Worktrees never live inside a repository. Each agent has one shared home for all
its accounts (`~/.claude/worktrees`, `~/.codex/worktrees`, `~/.grok/worktrees`,
`~/.t3/worktrees`); manual worktrees go in `~/worktrees`. The layout is
`<home>/<owner-repo>/<name>`, with `owner-repo` taken from the origin remote and
lowercased, and `GIT_WT_HOME` overrides the home. Keep at most 5 linked worktrees
per repository (hard limit 25) and remove each once its PR merges. A legacy
`.worktrees/` directory stays gitignored. Durable non-repo artifacts stay
under `~/.codex/artifacts/`. Never write helper scripts, PR snapshots, issue
bodies, or logs to the machine-wide temp directory.

Keep references **one level deep**: `SKILL.md` may point at files in `references/`, but those files must not chain on to further files (no A→B→C). Progressive disclosure breaks down when Claude has to follow a trail.

## Contract blocks for composable skills

Composable, action-oriented, or side-effecting skills should include a `## Contract`
section near the top of `SKILL.md`. Pure reference skills may skip this when the
description and body are enough.

Use this shape:

```markdown
## Contract

Inputs:
- Required context or arguments

Outputs:
- Artifacts or status the next skill can consume

Creates/Modifies:
- Local files, generated directories, or none

External Side Effects:
- Network calls, GitHub writes, deploys, publishes, or none

Confirmation Required:
- Actions that need explicit approval

Delegates To:
- Related skills to run next
```

Rules:

- Keep contracts factual and short.
- Put safety gates in the skill body, not only Claude-only frontmatter.
- Split skills at side-effect boundaries when a contract becomes ambiguous.
- For Shipshit.dev product initialization, route new product scaffolds through
  `npx @shipshitdev/v0` and use init/setup skills for customization or repair.

---

## Description quality bar

The description is the single most important field. Claude uses it to decide whether to activate the skill. It also gets truncated at 1,536 chars combined with `when_to_use`.

**Good:**

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents, forms, or document extraction.
```

**Bad:**

```yaml
description: Helps with PDFs.
```

Rules:

- Lead with the capability, follow with the trigger context
- Write in the third person ("Extracts text from PDFs…", not "I extract…" or "You can…")
- Include specific keywords users will say
- Max 1024 chars (spec limit); model-invoked skills stay within the **listing budget**: description ≤ 200 chars (aim for 180) and `when_to_use` ≤ 120 chars of trigger phrases the description lacks. Every model-invoked description loads into every session; the validator warns past the budget.
- No filler ("This skill is designed to help you...")
- **Model-invoked** descriptions keep rich trigger phrasing ("Use when the user wants…, mentions…, asks for…")
- **User-invoked** descriptions are human-facing one-liners. Put trigger lists in `when_to_use`, not in `description`

---

## Invocation architecture

Every skill in this repo is an explicit entry point: set
`disable-model-invocation: true`. The model never loads these skills on its own;
the user runs them by name (`/git cleanup`, `/run-qa`). The validator enforces
this.

Separate discoverability from authorization. Loading a skill grants no permission
to edit files, send messages, publish, deploy, or spend beyond the user's request.
Keep safety gates in the body, including a clear authorized mutation scope for
writing skills. Frontmatter controls discovery; it is not a permission boundary.

Because every skill here is user-only, the Skill tool cannot load one skill from
another. A skill that composes others runs each delegate by reading its sibling
`../<name>/SKILL.md` and following it; list those delegates under
`## Delegates To` with that instruction. Use `Recommend` (for example, Recommend
`/fix-ci`) for handoffs the user should start. Name upstream pstack or
mattpocock skills only as "when installed", and never assume a consumer has this
repository checked out.

**`allowed-tools` is an allowlist, not a sandbox.** Listing tools only bypasses their permission prompt; every unlisted tool is still callable and just prompts as normal. Narrowing `allowed-tools` does not lock a skill down — use `disallowed-tools`, deny rules, or hooks to actually block. For MCP tools, list the fully-qualified `ServerName:tool_name` so the grant resolves when multiple MCP servers are connected.

---

## Validation

Run the base-spec validator when you want to check the portable Agent Skills subset:

```bash
bunx skills-ref validate ./skills/my-skill
```

Checks:

- `name` matches directory name
- `name` format (lowercase, hyphens, length)
- `description` present and non-empty
- `metadata` values are strings (not lists or objects)

This validator does **not** understand Claude Code extension fields. For this repo, also run:

```bash
bun run validate
```

`scripts/validate.py` checks that `name` matches the directory, the description
length, `disable-model-invocation: true`, no `user-invocable: false`, no `model:`
or `effort:`, relative links, and concrete model IDs. `bun run test` covers the
validator and the skills' own script tests.

---

## Model references

Skills are model-agnostic playbooks. The harness that loads a skill supplies the
model — a skill must never assume or name one. Keeping skills model-free means a
new model generation touches only the per-repo routing block, never the skills.

- **No concrete model names anywhere in a skill** — not in the body, not in
  `references/`, not in `scripts/`. This covers tier+version IDs
  (`claude-sonnet-5`, `claude-3-7-sonnet-20250219`, `claude-opus-4.5`, `gpt-5.5`),
  dated snapshots, and a bare family name used as a routing key. They go stale on
  every release and pin the skill to one vendor.
- **Orchestrators are the only exception.** A skill that spawns sub-agents
  (fan-out review, multi-lens audit) may express **capability tiers** in prose —
  "cheapest/fastest tier for the fan-out finders, strongest available tier for the
  final verdict" — never a concrete model. The concrete tier→model mapping lives in
  the repo routing block (`CLAUDE.md`/`AGENTS.md`),
  so one per-repo file absorbs each model generation and each harness (Claude,
  Codex) maps the tiers to its own models.
- **Do not set `model:` or `effort:` in public skills.** Although Claude Code parses
  those extension fields, model and reasoning-effort selection belong to the active
  session or app configuration. See [Harness-Owned Execution Boundary](execution-boundary.md).
- **External tools are lanes, not models.** Naming Codex, `gh`, or a CLI as a
  dependency the skill shells out to is fine (it is a tool, like `git`). Naming the
  model that tool runs is not.
- **Enforced by the validator.** `scripts/validate.py` rejects version-pinned
  model IDs anywhere in a skill.

---

## Provenance

A skill authored in-house needs no provenance fields. A skill **derived from an
upstream** declares where it came from. Prefer installing the upstream directly
over deriving a copy here; this repo no longer vendors pstack or mattpocock skills.

Frontmatter (all under `metadata`):

```yaml
metadata:
  source: https://github.com/<org>/<repo>/blob/main/skills/<name>/SKILL.md
  upstream_repo: <org>/<repo>
  upstream_ref: main               # branch or tag tracked
  upstream_commit: <short-sha>     # commit synced at (or upstream_version)
  last_synced: "2026-07-04"        # ISO date
  license: <upstream SPDX id>
```

Plus a `## Upstream` section in the skill's `README.md` when `source` is set: a table mirroring the fields above, a **Local modifications** line,
and a **Checking for upstream changes** line.

The **Local modifications** line is what distinguishes the two derived kinds — no
separate frontmatter field is needed:

| Kind | Signal | Maintenance rule |
|------|--------|------------------|
| **Vendored** | Upstream is a genuine tool-vendor (anthropics, vercel-labs, cursor, openai, prisma, supabase…); README says "No behavioral changes beyond provenance metadata." | Re-sync from `source`; never hand-edit. Bump `upstream_commit` + `last_synced` on each pull. |
| **Adapted** | Upstream is an individual/community repo; README's Local modifications describes a substantive house-style rewrite. | Owned here. Rewrite to house style freely; `source` is attribution, not a sync target. |

Rules:

- Only **tool-vendor** upstreams qualify as vendored. A skill copied from an
  individual's repo is adapted — we own it and hold it to the full house style.
- Vendored skills are the sole skills exempt from a house-style rewrite. If a
  vendored skill needs a local fix, fix it upstream or promote it to adapted (take
  over maintenance) rather than silently diverging.
- On every re-sync, re-run the validator — a pull can reintroduce a model reference
  or a forbidden field.

---

## Versioning

Skills carry no individual version. The repository release version in
`package.json`, bumped by release-please, is the only version.

---

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills docs](https://code.claude.com/docs/en/skills)
- [agentskills/agentskills repo](https://github.com/agentskills/agentskills)
- [skills-ref validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- Writing craft and invocation split adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`writing-for-agents`, `.agents/invocation.md`, MIT)
