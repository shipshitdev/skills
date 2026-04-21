# Claude + Codex Skill Writing Guide

Skills in this library target **Claude Code and Codex together**. The shared baseline is the Agent Skills spec, and Claude-specific frontmatter extensions are allowed when they add real value.

## The Rule

**Write one SKILL.md that works cleanly in Codex and still exposes Claude-specific capabilities where useful.**

| Do | Don't |
|----|-------|
| "Read the file" | "Use the Read tool" |
| "Run the following command" | "Use the Bash tool to run" |
| "Edit the file" | "Use the Edit tool" |
| "Search for" | "Use the Grep tool" |
| "Find files matching" | "Use the Glob tool" |
| "Run the `other-skill` skill" | "Invoke `other-skill` using the Skill tool" |
| "This skill activates when..." | "Claude will use this skill when..." in universal instructions |
| "extends your capabilities" | "extends Claude's capabilities" in universal instructions |

## Frontmatter

Use Agent Skills frontmatter as the base. Codex relies on the base spec; Claude can also read its extension fields:

```yaml
---
name: skill-name
description: What the skill does and when to use it. Activates when...
license: MIT
metadata:
  version: "1.0.0"
  tags: "relevant, tags"
# Claude Code extensions are allowed below when needed
when_to_use: "extra trigger phrases for Claude"
disable-model-invocation: true
---
```

Keep `version`, `tags`, and custom metadata inside `metadata`. Claude Code extension fields may stay top-level when they are intentionally used: `when_to_use`, `disable-model-invocation`, `user-invocable`, `argument-hint`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, and `shell`.

## Writing Style

Use **imperative, action-oriented language**. This is the safest shared style across both CLIs:

- "Use when you need to..."
- "Run the command..."
- "Read the configuration file..."
- "Check for existing patterns before..."

Avoid third-person behavior claims in universal instructions ("Claude will...", "Codex will...") unless you are documenting a CLI-specific behavior in a clearly labeled section.

## Compatibility Model

| Layer | Claude Code | Codex |
|-------|-------------|-------|
| Agent Skills base spec | Yes | Yes |
| `allowed-tools` | Yes | Varies |
| Claude frontmatter extensions | Yes | No guarantee |
| Skill body instructions | Yes | Yes |
| Hooks via skill frontmatter | Yes | No guarantee |

Codex-safe rule: never make the skill depend on Claude-only frontmatter to be understandable or runnable. If Claude-only fields are ignored, the body should still work.

## When Platform-Specific Content Is Needed

Rare cases where a skill legitimately needs different behavior per platform (e.g., `agent-folder-init` scaffolding different config directories):

```markdown
<!-- PLATFORM-SPECIFIC-START: claude -->
Config directory: `~/.claude/`
<!-- PLATFORM-SPECIFIC-END: claude -->

<!-- PLATFORM-SPECIFIC-START: cursor -->
Config directory: `~/.cursor/`
<!-- PLATFORM-SPECIFIC-END: cursor -->
```

Use this sparingly. If more than 10% of a skill is platform-specific, consider splitting the skill or moving the CLI-specific material into `references/`.

## Skill-to-Skill References

When one skill needs to invoke another:

```markdown
Run the `session-documenter` skill to save session context.
```

Do NOT reference specific invocation mechanisms (`Skill tool`, `activate_skill`, etc.). Every platform knows how to run a skill by name.

For critical workflows, add a fallback:

```markdown
> If skill invocation is not available on your platform, follow the
> session-documenter workflow manually by reading its skill definition.
```

## Path References

Avoid hardcoded platform paths in universal instructions. If a skill needs to reference its own files, use relative paths:

```markdown
See `references/full-guide.md` for detailed documentation.
Run `scripts/scaffold.py` to generate the project structure.
```

## Progressive Disclosure

All platforms benefit from keeping skills concise:

1. **Metadata** (frontmatter) — always in context (~100 words)
2. **SKILL.md body** — loaded when skill triggers (aim for <500 lines)
3. **References/scripts** — loaded on demand

Move detailed content to `references/` early. Prefer examples over explanations.

## Checklist for New Skills

- [ ] No tool-name references (Read tool, Bash tool, etc.)
- [ ] No platform-name coupling in universal instructions
- [ ] No hardcoded platform paths
- [ ] Imperative writing style throughout
- [ ] Claude-only frontmatter is intentional and documented by the skill body
- [ ] Standard bash commands (portable across Unix/macOS)
- [ ] Relative paths for bundled resources
- [ ] Under 500 lines for SKILL.md body
