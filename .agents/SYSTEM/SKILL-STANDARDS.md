# Skill Standards

This repo follows the [Agent Skills open standard](https://agentskills.io/specification) as the base spec, extended with Claude Code-specific fields. Every skill must comply with both layers.

---

## Frontmatter reference

### Base spec (agentskills.io) — applies to all agents

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | **Yes** | 1–64 chars. Lowercase letters, numbers, hyphens. No leading/trailing/consecutive hyphens. Must match directory name. |
| `description` | **Yes** | 1–1024 chars. Describes what the skill does AND when to use it. Front-load key use case. |
| `license` | No | License name or reference to bundled LICENSE file. |
| `compatibility` | No | 1–500 chars. System requirements: target agent, required packages, network needs. Omit if no special requirements. |
| `metadata` | No | Map of `string → string`. Use for `version`, `tags`, `author`, and any extra data. |
| `allowed-tools` | No | Space-separated pre-approved tools. Experimental — support varies by agent. |

### Claude Code extensions — Claude-only fields

| Field | Purpose |
|-------|---------|
| `when_to_use` | Extra trigger phrases appended to `description` in skill listing. Combined with `description`, capped at 1,536 chars. |
| `disable-model-invocation` | `true` = only user can invoke (no auto-trigger). Use for destructive/side-effect skills. |
| `user-invocable` | `false` = hides from `/` menu. Use for background knowledge skills. |
| `model` | Override model for this skill. |
| `effort` | Override effort level: `low`, `medium`, `high`, `xhigh`, `max`. |
| `context` | `fork` = run in isolated subagent. |
| `agent` | Subagent type when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or custom. |
| `hooks` | Lifecycle hooks scoped to this skill. |
| `paths` | Glob patterns that limit when skill auto-activates. |
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
allowed-tools: Bash(gh *) Bash(git *)
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
- Include specific keywords users will say
- Max 1024 chars (spec limit)
- No filler ("This skill is designed to help you...")

---

## When to add Claude Code extensions

| Field | Add when... |
|-------|-------------|
| `when_to_use` | Description alone doesn't cover all trigger phrases |
| `disable-model-invocation: true` | Skill has side effects (file writes, git ops, GitHub API calls, deploys) |
| `user-invocable: false` | Skill is background knowledge, not an action users invoke |
| `context: fork` | Skill does independent research/exploration that shouldn't see conversation history |
| `allowed-tools` | Skill needs specific tools without per-use permission prompts |
| `effort: high` | Skill requires deep reasoning (architecture decisions, complex debugging) |
| `paths` | Skill only applies to specific file types or directories |

---

## plugin.json format

Required for distribution via `npx skills add`. Generated by `bun run generate:plugin`.

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Short description (shown in npx skills registry). Max ~100 chars.",
  "author": {
    "name": "Ship Shit Dev",
    "email": "hello@shipshit.dev",
    "url": "https://github.com/shipshitdev"
  },
  "license": "MIT",
  "skills": "."
}
```

`"skills": "."` means the plugin root is the skill directory itself.

---

## Validation

Run the agentskills validator:

```bash
bunx skills-ref validate ./skills/my-skill
```

Checks:

- `name` matches directory name
- `name` format (lowercase, hyphens, length)
- `description` present and non-empty
- `metadata` values are strings (not lists or objects)

Claude Code also warns if `SKILL.md` exceeds 500 lines.

---

## Versioning

Versions live in `metadata.version`. Use semver:

- `1.0.0` — initial stable
- `1.1.0` — new capability, backwards compatible
- `2.0.0` — breaking change to workflow or output format

Bump version in both `SKILL.md` (`metadata.version`) and `plugin.json` (`version`) when publishing.

---

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills docs](https://code.claude.com/docs/en/skills)
- [agentskills/agentskills repo](https://github.com/agentskills/agentskills)
- [skills-ref validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
