---
name: skill-capture
description: Turns workflows and hard-won knowledge from a conversation into reusable SKILL.md files. Use when asked to save something as a skill, or after a complex procedure succeeds.
metadata:
  version: "2.2.4"
  tags: "skills, capture, automation, knowledge-management"
when_to_use: "make this reusable, save this pattern"
---

# Skill Capture

## When to activate

- **Explicit requests:** "save this as a skill", "make this a skill", "this workflow should be reusable", "capture this", "save this pattern".
- **Completion signals:** a complex problem solved after several iterations; a multi-step procedure that finally ran; domain knowledge found through research; a code pattern other projects could use.
- **Learning moments:** "this was tricky to figure out", "I wish I knew this earlier", "this should be documented".

A capture request authorizes the matching skill edits. A completion signal alone authorizes a proposal, not persistence or tracker submissions. Stay inside the user's scope and ask before consequential changes outside it.

## Process (5 phases, in order)

### 1. Identification

Review the conversation for capturable content:

| Category | Example |
|----------|---------|
| Workflows | Multi-step procedures that took iterations to perfect |
| Domain knowledge | Information requiring research or expertise |
| Problem solutions | Approaches that resolved complex issues |
| Code patterns | Reusable patterns that could help other projects |
| Decision rationale | Architectural choices with clear reasoning |

Ask: Is it generalizable beyond this project? Would another agent session benefit? Did it take multiple iterations? Is it non-obvious procedural knowledge?

### 2. Destination planning

1. Check whether an existing skill should be updated: glob the repo's skills directory for `*/SKILL.md` and read related skills for overlap.
2. Otherwise create a new skill with a descriptive kebab-case name in its own directory (`<skills-dir>/<skill-name>/`).

Skill or rule?

| Create a skill | Capture a rule |
|----------------|----------------|
| Workflow with multiple steps | Single preference statement |
| Procedural knowledge | "always/never do X" |
| Domain expertise | Style/format preferences |
| Code patterns with context | Import/naming conventions |

If it is a rule or preference, use a rules-capture skill if available; otherwise add it to the project's instructions file (CLAUDE.md / AGENTS.md) instead of creating a skill.

### 3. Content drafting

Transform the conversation into SKILL.md format:

```markdown
---
name: <skill-name>
description: <What it does + "Use when ..." triggers, one line>
---

# <Skill Title>

<Brief description of the purpose>

## When to Use

<Clear triggers>

## Process

<Step-by-step workflow>

## Examples

<Concrete examples>

## Integration

<How it works with other skills, if applicable>
```

Principles: imperative form ("Do X", not "You should do X"); specific triggers; concrete examples; reference bundled resources.

### 4. Distillation

1. Extract the final approach; capture only what worked, not the failed attempts.
2. Generalize; remove project-specific details that do not apply broadly.
3. Add context; explain why an approach works, not just what to do.
4. Include examples, good and bad where helpful.

Checklist: project-specific paths and names removed; hardcoded values generalized; non-obvious steps explained; imperative language throughout.

### 5. Verification

| Check | Requirement |
|-------|-------------|
| Length | Under 500 lines (move large content to `references/`) |
| Frontmatter | Valid YAML with `name` and `description` |
| Completeness | Every section has meaningful content |
| Actionability | Instructions specific enough to follow |
| Formatting | Matches the existing skills in the repo |

Validate with the repo's skill validator if one exists (for example `scripts/package_skill.py skills/<skill-name>` from the skill-creator skill); otherwise check the table by hand. Add a plugin manifest only if the repo's other skills have one.

## What to capture

**Good candidates:** multi-iteration workflows; domain knowledge that required research; problem-solving approaches that worked; reusable code patterns; architectural decision rationale; tool/service integration patterns; technology-specific debugging approaches.

**Do NOT capture:** one-off project-specific solutions; trivial fixes or obvious patterns; information documented elsewhere; sensitive or proprietary information; incomplete workflows still being refined; preferences without procedural value (record as a rule).

## Related skills (if available)

| Skill | Role |
|-------|------|
| rules-capture | Captures preferences and rules; this skill handles multi-step procedures |
| skill-creator | Creation patterns and validation |
| retro | Reviews a finished session for friction and routes skill candidates back here |

## Example

**Context:** the user spent 30 minutes debugging a NestJS queue integration; the fix needed specific configuration patterns.

**User:** "This was a pain to figure out. Let's save this for next time."

**Agent:**

```
I'll capture this. Capturable knowledge:
- NestJS Bull queue configuration pattern
- Redis connection handling for queues
- Processor registration requirements

The existing nestjs-queue-architect skill covers queue setup but not this
debugging pattern. I'll read it, then add a "Troubleshooting" section
documenting the Redis connection requirements and common error patterns.
```
