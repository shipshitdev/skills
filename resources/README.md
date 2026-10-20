# resources/

First-hand reference material for working in this repo. Unlike `.agents/memory/system/` (this repo's own operating standards), `resources/` holds **extracted upstream guidance** — what Anthropic and OpenAI themselves publish — kept separate so the source of truth is unambiguous.

## skill-authoring/

Official skill-authoring guidance, extracted from 13 first-hand vendor sources and read on 2026-06-12. Every rule links back to its source URL.

| File | What's in it |
|------|--------------|
| [anthropic.md](skill-authoring/anthropic.md) | Anthropic's rules — Claude Code / Claude API / claude.ai. Frontmatter, naming, descriptions, structure, progressive disclosure, invocation, tool permissions, references/scripts, testing, anti-patterns. |
| [codex.md](skill-authoring/codex.md) | OpenAI Codex's rules, with the divergences from Anthropic called out. |
| [frontmatter-field-spec.md](skill-authoring/frontmatter-field-spec.md) | Field-by-field reference table (base spec + Claude extensions) with the constraints that bite. |
| [checklist.md](skill-authoring/checklist.md) | One pass/fail checklist to run against any SKILL.md before shipping, plus live known-issues. |
| [sources.md](skill-authoring/sources.md) | Annotated bibliography of the 13 primary sources. |

## How to use

- Writing or reviewing a skill: start with [checklist.md](skill-authoring/checklist.md), reach for [frontmatter-field-spec.md](skill-authoring/frontmatter-field-spec.md) on field questions.
- This repo's own conventions (platform-neutral writing, Contract blocks, validation) live in `.agents/memory/system/` and take precedence for repo work; `resources/` is the upstream ground truth those conventions are built on.

## Maintenance

The skill-authoring docs were generated from a research pass and are dated. The platforms move — fields get added, bugs get fixed. Re-verify the time-sensitive items in [checklist.md](skill-authoring/checklist.md#open-questions--known-issues) before relying on them, and re-run the research when the date drifts more than a few months.
