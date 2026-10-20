# Skills Repo — Agent Instructions

This is the shipshitdev/skills repo: 14 user-invoked agent skills for Claude
Code, Codex, and Cursor.

## Repo Structure

- `skills/` — every skill (`SKILL.md` plus optional `references/`, `scripts/`, `tests/`)
- `scripts/` — `validate.py` and its tests
- `resources/` — extracted upstream skill-authoring guidance
- `.agents/` — repo memory and standards

## Rules

- Follow `.agents/memory/system/skill-standards.md`.
- Every skill sets `disable-model-invocation: true` and never `user-invocable: false`.
- Skill names are one word. Related workflows are actions under one router skill
  (`/git pr`): the router's `SKILL.md` dispatches on the first word to
  `references/<action>.md`.
- A skill composes another by reading its playbook from the installed skills
  directory (`<router>/references/<action>.md` or `<name>/SKILL.md`); the Skill
  tool cannot load user-only skills.
- No `model:`, `effort:`, version metadata, or concrete model IDs in skills.
- Name upstream pstack or mattpocock skills only as "when installed"; never vendor them.
- Run `bun run lint`, `bun run validate`, and `bun run test` before committing.

## Code Standards

- Conventional commits: `fix:`, `feat:`, `refactor:`, `chore:`, `docs:`
- Never commit secrets (`.env`, API keys)
- Bun only, never npm/yarn/pnpm

## Before Editing Skills

1. Read the SKILL.md you'll modify
2. Find 3+ similar skills to follow their patterns
3. Check `.agents/memory/memory.md` for repo decisions
