# Do and Don't — Skills Repo

last_verified: 2026-10-20

## DO

- DO put every skill in `skills/<skill-name>/SKILL.md` — one flat directory per skill
- DO match `name:` to the directory name exactly
- DO set `disable-model-invocation: true` on every skill
- DO keep `description:` between 1-1024 chars and front-load the use case
- DO compose skills by reading the sibling `../<name>/SKILL.md`
- DO write platform-neutral, imperative instructions
- DO keep SKILL.md under 500 lines; move detail into `references/`
- DO run `bun run lint`, `bun run validate`, and `bun run test` before committing
- DO use conventional commits and let the pre-commit hook run
- DO scrub hardcoded paths and project names from imported material

## DON'T

- DON'T set `user-invocable: false`, `model:`, `effort:`, or a version
- DON'T name concrete model IDs anywhere in a skill
- DON'T vendor or rewrite pstack or mattpocock skills — install them upstream
- DON'T create per-platform copies (`.claude/skills/`, `.codex/skills/`)
- DON'T add `commands/`, bundles, or generated catalogs back
- DON'T use npm/yarn/pnpm — Bun only
- DON'T commit `node_modules/`, `.agents/sessions/`, `.env` files, or secrets
- DON'T skip hooks (`--no-verify`) or force-push to master
- DON'T run `npx skills add ~/.agents/skills` — it treats the install target as
  the source and wipes it
