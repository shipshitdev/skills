# Universal Skill Writing Guide

Skills in this library are **platform-agnostic by default**. One SKILL.md works on Claude Code, Codex, Cursor, OpenClaw, Gemini, and any future agent that supports the skills.sh format.

## The Rule

**Write for any agent, not a specific one.**

| Do | Don't |
|----|-------|
| "Read the file" | "Use the Read tool" |
| "Run the following command" | "Use the Bash tool to run" |
| "Edit the file" | "Use the Edit tool" |
| "Search for" | "Use the Grep tool" |
| "Find files matching" | "Use the Glob tool" |
| "Run the `other-skill` skill" | "Invoke `other-skill` using the Skill tool" |
| "This skill activates when..." | "Claude will use this skill when..." |
| "extends your capabilities" | "extends Claude's capabilities" |

## Frontmatter

Use the universal format. All platforms read `name` and `description`:

```yaml
---
name: skill-name
description: What the skill does and when to use it. Activates when...
version: 1.0.0
tags:
  - relevant
  - tags
---
```

No platform-specific fields (`license`, `metadata.short-description`) — these are handled by the distribution tooling, not the skill content.

## Writing Style

Use **imperative, action-oriented language**. This is the most universal style across all platforms:

- "Use when you need to..."
- "Run the command..."
- "Read the configuration file..."
- "Check for existing patterns before..."

Avoid third-person ("Claude will...", "The agent should...") and passive voice.

## Platform Capabilities Matrix

| Capability | Claude Code | Codex | Cursor | OpenClaw | Gemini |
|-----------|-------------|-------|--------|----------|--------|
| Skills (SKILL.md) | Yes | Yes | Yes | Yes | Yes |
| Slash commands | Yes | Yes | Yes (IDE) | Yes | Yes |
| Subagents | Yes | Limited | No | Varies | Varies |
| File read/write | Yes | Yes | Yes (IDE) | Yes | Yes |
| Bash execution | Yes | Sandboxed | Yes | Yes | Yes |
| Skill-to-skill invocation | Yes (Skill tool) | Yes | Limited | Varies | Yes |
| Hooks | Yes | No | No | Varies | No |
| MCP servers | Yes | No | Yes | Varies | Yes |

## When Platform-Specific Content IS Needed

Rare cases where a skill legitimately needs different behavior per platform (e.g., `agent-folder-init` scaffolding different config directories):

```markdown
<!-- PLATFORM-SPECIFIC-START: claude -->
Config directory: `~/.claude/`
<!-- PLATFORM-SPECIFIC-END: claude -->

<!-- PLATFORM-SPECIFIC-START: cursor -->
Config directory: `~/.cursor/`
<!-- PLATFORM-SPECIFIC-END: cursor -->
```

Use this sparingly. If more than 10% of a skill is platform-specific, consider whether it should be split into separate skills.

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

Avoid hardcoded platform paths (`~/.claude/skills/`, `~/.codex/skills/`). If a skill needs to reference its own files, use relative paths:

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
- [ ] No platform-name references (Claude, Codex) in instructions
- [ ] No hardcoded platform paths
- [ ] Imperative writing style throughout
- [ ] Standard bash commands (portable across Unix/macOS)
- [ ] Relative paths for bundled resources
- [ ] Under 500 lines for SKILL.md body
