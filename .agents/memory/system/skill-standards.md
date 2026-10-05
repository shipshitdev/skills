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
| `metadata` | No | Map of `string → string`. Use for `version`, `tags`, `author`, and any extra data. |
| `allowed-tools` | No | Space-separated **auto-approve allowlist** — bypasses the per-use prompt for listed tools. NOT a sandbox: unlisted tools stay callable and fall through to normal permission prompts. Experimental — support varies by agent. |

### Claude Code extensions — Claude-only fields

| Field | Purpose |
|-------|---------|
| `when_to_use` | Extra trigger phrases appended to `description` in skill listing. Combined with `description`, capped at 1,536 chars. |
| `disable-model-invocation` | `true` keeps an entry point user-only. Reusable engines omit it and enforce action authorization in their body. |
| `user-invocable` | `false` = hides from `/` menu. Use for background knowledge skills. |
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
  version: "1.0.0"
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
| `version: 1.0.0` (top-level) | `metadata:\n  version: "1.0.0"` | `version` is not a spec field — must be inside `metadata` |
| `tags:\n  - foo\n  - bar` (top-level) | `metadata:\n  tags: "foo, bar"` | Same. `metadata` values must be strings, not lists |
| `auto_activate: true` | Remove entirely | Not in spec, ignored by all agents |
| `auto_trigger: false` | Remove entirely | Not in spec, ignored by all agents |
| Empty `compatibility` | Omit the field | Only include if skill has real requirements |
| `description: Helps with X.` | Full sentence with trigger context | Too short, won't auto-activate reliably |

---

## Skill directory structure

```
skills/my-skill/
├── SKILL.md           # Required. Metadata + instructions. Keep under 500 lines.
├── plugin.json        # Required for distribution via npx skills add.
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

Worktrees stay at `<repo>/.worktrees/<name>`. Durable non-repo artifacts stay
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

Separate discoverability from authorization. Loading a skill grants no permission
to edit files, send messages, publish, deploy, or spend beyond the user's request.

| Kind | Frontmatter | Composition |
|------|-------------|-------------|
| **Explicit entry point** | `disable-model-invocation: true` | The human selects the workflow. Keep advisory maps and open-ended session starters here. |
| **Reusable engine** | omit `disable-model-invocation` | A user or another workflow may invoke it within the authorized task. Its body owns action gates. |
| **Command router** | `user-invocable: false`, omit `disable-model-invocation` | Behind a `commands/*.md` front door (`*-dispatch`, `ask-dev-loop`). The command is the user entry and is itself user-only; the model must be able to load the router the command names. |

**Execution routers** such as `/test run` select a declared engine and pass the
requested mode, target, authorized actions, and restrictions. Existing explicit
authorization satisfies an action gate within that scope; ask only for a missing
or expanded authorization. A read-only/report-only request stays read-only across
all delegates. Delegation never expands host, provider, cost, publication, or
production permissions. A test-run request does not authorize repairs.

**Advisory routers** such as `/ask` return a recommendation. `interview` and
`shape` stop at their promised brief. Their stopping point follows their output
contract, not a catalog-wide prohibition on composition. Recommend an explicit
entry point instead of pretending to invoke one the harness hides from the model.

Pick engine discoverability whenever another skill must run the workflow.
Keep safety gates in the body, including a clear authorized mutation scope for
writing engines. Frontmatter controls discovery; it is not a permission boundary.
Resolve dependencies through the active skill catalog, then resolve resources
relative to the selected skill's installed directory. Never assume a consumer has
this repository's `skills/` directory or repository-management meta-skills.

Use direct imperative routes (for example, Run the `engine-name` skill) for actual
composition, and `Recommend` for a handoff. The validator checks these explicit
execution routes and leading target lists in `Delegates To:` bullets, including
comma-joined lists across wrapped lines. Start advisory declarations with
`Recommend` and resource declarations with `File pointer`. Mode names in an
explanation and fenced examples are not execution dependencies.

---

## Writing craft

Skills are documents an agent runs, not essays. These levers keep a run predictable — the same *process* every time, not the same output. Apply them to new and edited skills. Catalog-wide passes are fine when Vincent approves one (the 2026-10-03 listing-budget pass). Keep Contract blocks. Longer-form levers (two loads, co-location, sprawl, split-by-sequence, environment-as-cache, sediment) live in `skills/skill-creator/references/writing-for-agents.md`.

**Leading words.** Collapse a restated idea into one pretrained token the agent already thinks with (`frontier`, `seam`, `tight`, `red`). Repeat the token; do not re-explain the sentence. A coined word recruits no priors — prefer a word the model already knows.

**Completion criteria.** Every step ends on a checkable bound ("frontier empty", "the narrow test fails for the missing behavior"). Vague bounds ("understanding reached") invite premature completion. Sharpen the bound first; split across a context boundary only if the bound stays fuzzy *and* the agent rushes.

**Context pointers.** A `description` (and any always-loaded line that names out-of-context material) is a pointer: what the material is, plus the branches that should load it. Front-load the leading word. One trigger per genuine branch. Cut identity the body already carries.

**Information hierarchy.** Inline what every branch needs. Disclose behind a pointer (`references/`) what only some branches reach. Keep `SKILL.md` under 500 lines. References stay one level deep.

**Prune no-ops.** Delete a sentence that does not change default model behavior. The test is behavioral, not reader-relative: run the skill; if the line never bites, remove the whole sentence.

**Prompt the positive.** State the target behavior ("write one-line comments"). Negation drags the forbidden behavior into context and makes it more available. A prohibition earns its place only as a hard guardrail that cannot be phrased positively, and then only paired with the positive target.

---

## When to add Claude Code extensions

| Field | Add when... |
|-------|-------------|
| `when_to_use` | Description alone doesn't cover all trigger phrases |
| `disable-model-invocation: true` | Explicit entry points and advisory workflows. Reusable writing engines stay callable and require scoped authorization in their body. |
| `user-invocable: false` | Skill is background knowledge, not an action users invoke |
| `context: fork` | Skill does independent research/exploration that shouldn't see conversation history (must have an actionable task — guidelines-only forks return empty) |
| `allowed-tools` | You want to skip the per-use prompt for tools the skill calls repeatedly. Remember it only *auto-approves*, it does not restrict — see note below |
| `disallowed-tools` | You need to actually **block** a tool while the skill runs (e.g. keep an autonomous loop from calling `AskUserQuestion`) |
| `paths` | ~~Skill only applies to specific file types~~ — avoid until issue #49835 is fixed (sets the skill undiscoverable); use nested `.claude/skills/` dirs instead |

**`allowed-tools` is an allowlist, not a sandbox.** Listing tools only bypasses their permission prompt; every unlisted tool is still callable and just prompts as normal. Narrowing `allowed-tools` does not lock a skill down — use `disallowed-tools`, deny rules, or hooks to actually block. For MCP tools, list the fully-qualified `ServerName:tool_name` so the grant resolves when multiple MCP servers are connected.

---

## plugin.json format

Required for distribution via `npx skills add`. Keep this committed file synced with the skill frontmatter.

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Short description (shown in npx skills registry). Max 100 chars.",
  "author": {
    "name": "Ship Shit Dev",
    "email": "hello@shipshit.dev",
    "url": "https://shipshit.dev"
  },
  "license": "MIT",
  "skills": "."
}
```

`"skills": "."` means the plugin root is the skill directory itself.

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
./scripts/validate-skill-sync.sh
```

That repo validator enforces the shared Claude Code + Codex rules and allows the approved Claude extension fields.

---

## Model references

Skills are model-agnostic playbooks. The harness that loads a skill supplies the
model — a skill must never assume or name one. 146 of this repo's skills already
carry zero model references; keeping it that way means a new model generation
touches only the per-repo routing block, never the skills.

- **No concrete model names anywhere in a skill** — not in the body, not in
  `references/`, not in `scripts/`. This covers tier+version IDs
  (`claude-sonnet-5`, `claude-3-7-sonnet-20250219`, `claude-opus-4.5`, `gpt-5.5`),
  dated snapshots, and a bare family name used as a routing key. They go stale on
  every release and pin the skill to one vendor.
- **Orchestrators are the only exception.** A skill that spawns sub-agents
  (fan-out review, multi-lens audit) may express **capability tiers** in prose —
  "cheapest/fastest tier for the fan-out finders, strongest available tier for the
  final verdict" — never a concrete model. The concrete tier→model mapping lives in
  the repo routing block (`CLAUDE.md`/`AGENTS.md`, written by `setup-agent-routing`),
  so one per-repo file absorbs each model generation and each harness (Claude,
  Codex) maps the tiers to its own models.
- **Do not set `model:` or `effort:` in public skills.** Although Claude Code parses
  those extension fields, model and reasoning-effort selection belong to the active
  session or app configuration. See [Harness-Owned Execution Boundary](execution-boundary.md).
- **External tools are lanes, not models.** Naming Codex, `gh`, or a CLI as a
  dependency the skill shells out to is fine (it is a tool, like `git`). Naming the
  model that tool runs is not.
- **Enforced by the validator.** `scripts/validate-skill-sync.sh` hard-errors on
  version-pinned model IDs anywhere in a skill, and on bare tier names
  (`sonnet`/`opus`/`haiku`) outside a `model:`/`model =` assignment. Harness-owned
  execution parameters (`model:`/`effort:` keys) in reusable content are flagged
  as warnings.

---

## Provenance

A skill authored in-house needs no provenance fields. A skill **derived from an
upstream** declares where it came from, so the rewrite-vs-resync decision is
mechanical. The convention is enforced by `check_provenance()` in
`scripts/validate-skill-sync.sh` and used by derived skills in this catalog.

Frontmatter (all under `metadata`):

```yaml
metadata:
  version: "1.0.0"
  source: https://github.com/<org>/<repo>/blob/main/skills/<name>/SKILL.md
  upstream_repo: <org>/<repo>
  upstream_ref: main               # branch or tag tracked
  upstream_commit: <short-sha>     # commit synced at (or upstream_version)
  last_synced: "2026-07-04"        # ISO date; validator warns if >90 days old
  license: <upstream SPDX id>
```

Plus a `## Upstream` section in the skill's `README.md` (validator requires it when
`source` is set): a table mirroring the fields above, a **Local modifications** line,
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

All public and repo-maintenance skills share the repository release version
from `package.json`.
Set `metadata.version` and `plugin.json.version` to that exact value (currently
`2.2.2`). Do not assign independent major, minor or patch versions to a skill.
Repository releases use semver; release automation owns the next release number.

- Run `bun run version:sync` to align canonical skill and plugin metadata.
- `bun run version:check` checks every pair against `package.json.version`; skill
  instruction edits do not require an individual version increment.
- `bun run marketplace:generate` synchronizes versions before generating bundles
  and marketplace entries. Release automation uses this same path.
- `bun run validate` still rejects mismatched skill/plugin metadata or invalid
  descriptions. Shared versions do not replace instruction or runtime review.
- Version synchronization advances Pstack fingerprints only when the destination's
  pre-edit bytes match the accepted hash. Unreviewed body changes keep their old
  fingerprints and remain blocked at the adaptation review gate.

---

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills docs](https://code.claude.com/docs/en/skills)
- [agentskills/agentskills repo](https://github.com/agentskills/agentskills)
- [skills-ref validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- Writing craft and invocation split adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`writing-for-agents`, `.agents/invocation.md`, MIT)
