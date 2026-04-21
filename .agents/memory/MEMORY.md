# Skills Repo Memory

last_verified: 2026-04-21

## What This Repo Is

Public skills library at `shipshitdev/skills`. 155 skills, 26 commands, 14 bundles. Installable via `npx skills add shipshitdev/skills --skill <name>`. Works with Claude Code, Codex, Cursor, OpenClaw, Gemini.

Published as `@agenticdev/*` packages via generated `plugins/` directory. Marketplace catalog at `.claude-plugin/marketplace.json`.

## Repo Identity

- **Name:** ship-shit-dev-library
- **Owner:** Vincent (decod3rs) — solo founder, zero-code workflow
- **License:** MIT
- **Runtime:** Bun (never npm/yarn/pnpm)
- **Linting:** markdownlint (markdown), biome (JSON/JS), shellcheck (bash)
- **CI:** GitHub Actions on push to master — regenerates bundles + marketplace

## Numbers (snapshot 2026-04-21)

| Asset | Count | Location |
|-------|-------|----------|
| Skills | 155 | `skills/<name>/SKILL.md` |
| Commands | 26 | `commands/<name>.md` |
| Bundles | 14 | `bundles/<bundle>/plugin.json` |
| Scripts | 15 | `scripts/` |
| Prompts | 1 | `prompts/prd-interview.md` |

## Architecture Decisions

### Single-Source Skills (2026-02-04)

One `skills/` directory at root. No per-platform copies. Platform-neutral writing: no tool names, imperative style.

### Agent Skills Spec Compliance (2026-04-21)

Follow agentskills.io/specification as base. Claude Code extensions (`when_to_use`, `disable-model-invocation`, `allowed-tools`, etc.) added on top. `version`/`tags` go inside `metadata:` block as strings, not top-level. See `.agents/SYSTEM/SKILL-STANDARDS.md`.

### External Skills Imported (2026-04-21)

All referenced external repos now internal — no external dependencies:

| Source | Skills Imported |
|--------|----------------|
| coreyhaines31/marketingskills | 14 CRO/SEO/marketing skills |
| vercel-labs/agent-skills | vercel-react-best-practices, web-design-guidelines |
| trailofbits/skills | 10 security audit skills |
| expo/skills | 10 expo-* mobile skills |
| resend/resend-skills + email-best-practices | 5 resend-* email skills |
| sickn33/antigravity-awesome-skills | 20 cherry-picked skills (JS, NestJS, Prisma, security, marketing, etc.) |

### Consolidation Decisions (2026-04-21)

| Decision | Rationale |
|----------|-----------|
| Keep copywriter + copywriting separate | copywriter = brand-aware persona, copywriting = guardrailed landing page copy |
| Merge clean-code + code-refactoring-refactor-clean → refactor-code | refactor-code is best-developed; others are weaker duplicates |
| Keep all 5 security skills | Distinct: expert persona, audit workflow, API-specific, backend impl, frontend impl |
| Keep react-patterns + react-refactor + react-component-performance | Cleanly separated by concern |
| Keep all expo-*/resend-*/static-analysis-* families | Non-overlapping topics |

## Known Issues

None currently tracked.

## Key Files

- `.agents/SYSTEM/SKILL-STANDARDS.md` — authoritative spec doc
- `.agents/SYSTEM/SKILL-MANAGEMENT.md` — workflow guide
- `scripts/validate-skill-sync.sh` — validation script
- `scripts/generate-manifest.js` — manifest generation
- `scripts/generate-plugin.js` — plugin.json generation
- `.claude-plugin/marketplace.json` — full marketplace catalog (generated)
- `.github/workflows/generate-bundles.yml` — CI pipeline
