# Skills Repo Memory

last_verified: 2026-08-14

## What This Repo Is

<!-- catalog-summary:start -->
Public skills library at `shipshitdev/skills`. Installable via `npx skills add shipshitdev/skills --skill <name>`. Works with Claude Code, Codex, Cursor, OpenClaw, and Gemini.

Generated catalog: **188 skills · 30 commands · 13 bundles · 201 plugins**.
<!-- catalog-summary:end -->

Published through committed marketplace bundles in `bundles/` and the generated `.claude-plugin/marketplace.json` catalog. The old generated `plugins/` package tree is retired.

## Repo Identity

- **Name:** ship-shit-dev-library
- **Owner:** Vincent (decod3rs) — solo founder, zero-code workflow
- **License:** MIT
- **Runtime:** Bun (never npm/yarn/pnpm)
- **Linting:** markdownlint (markdown), biome (JSON/JS), shellcheck (bash)
- **CI:** GitHub Actions on push to master — regenerates bundles + marketplace

## Generated Catalog Counts

<!-- catalog-counts:start -->
| Asset | Count | Canonical source |
|---|---:|---|
| Skills | 188 | `skills/*/SKILL.md` |
| Commands | 30 | `commands/*.md` |
| Bundles | 13 | `scripts/plugin-categories.json` |
| Plugins | 201 | skills + bundles |
<!-- catalog-counts:end -->

## Architecture Decisions

### Single-Source Skills (2026-02-04)

One `skills/` directory at root. No per-platform copies. Platform-neutral writing: no tool names, imperative style.

### Agent Skills Spec Compliance (2026-04-21)

Follow agentskills.io/specification as base. Claude Code extensions (`when_to_use`, `disable-model-invocation`, `allowed-tools`, etc.) added on top. `version`/`tags` go inside `metadata:` block as strings, not top-level. See `.agents/memory/system/skill-standards.md`.

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

### Session Logs Are Local-Only (2026-06-19)

`.agents/sessions/` is **gitignored** in this repo — session logs stay local,
not committed (public open-source repo). This overrides the global ritual that
commits session logs per-repo. Do NOT `git add -f` session docs here. The
durable equivalent that *does* get committed is decisions in
`.agents/memory/*.md`. (Fixed a case bug: the rule was `.agents/SESSIONS/` and
silently matched nothing on Linux; 10 previously-tracked session files were
`git rm --cached`.)

### EARS Acceptance Criteria (2026-06-19)

PRD/spec skills standardize acceptance criteria on **EARS** (Easy Approach to
Requirements Syntax): `WHEN/WHILE/WHERE/IF … THE SYSTEM SHALL …`, or a bare
`THE SYSTEM SHALL …`. `prd-quality-gate` validates each Acceptance Criteria
bullet against this grammar (regex `^\s*(\d+\.\s*)?(WHEN|WHILE|WHERE|IF|THE
SYSTEM)\b.*\bSHALL\b`); draft lint may warn; execution readiness is blocking (see the prepared-delivery decision below). The canonical
verifiable-outcomes section is `Acceptance Criteria` (the former
`Success Criteria` in `prd-writer`/`feature-intake` was renamed/merged — they
are now one EARS section; testing bars live in `Verification Plan`). Applies to
`prd-writer`, `prd-quality-gate`, `feature-intake`, `spec-first`,
`prd-task-creator`. Rationale: skills are read by AI coding agents, where vague
prose criteria cause drift; EARS is the de-facto agent-spec grammar (Kiro-origin,
not a ratified standard — the gate regex is the single point to adjust if it shifts).

### Consolidation Decisions (2026-04-21)

| Decision | Rationale |
|----------|-----------|
| Move content/GTM skills out of Shipshit | Shipshit is dev-workflow focused; content and GTM strategy skills live in Genfeed |
| Merge clean-code + code-refactoring-refactor-clean → refactor-code | refactor-code is best-developed; others are weaker duplicates |
| Keep all 5 security skills | Distinct: expert persona, audit workflow, API-specific, backend impl, frontend impl |
| Keep react-patterns + react-refactor + react-component-performance | Cleanly separated by concern |
| Keep all expo-*/resend-*/static-analysis-* families | Non-overlapping topics |

### Pstack consolidation (2026-09-05)

Maintain one canonical Shipshit implementation. Open Pstack supplies the portable
base; Cursor Pstack is independently tracked for original-only capabilities.
Pinned archives and exhaustive source mappings live in upstream/pstack/. Runtime
scripts ship in skills/pstack/scripts/; principles and platform adapters are
installed resources, not duplicate skill catalogs. Existing deslop modes and tdd
contributions stay canonical. Benny and Bot UI are dormant, explicit setup
capabilities. Installing a skill does not activate their routines or services.

Use scripts/pstack-sync.py to verify accepted snapshots and stage reviewed
upstream candidates. Never advance accepted source commits or overwrite local
adaptations automatically. Review after major model/harness releases while
preserving user-owned provider routing. See upstream/pstack/README.md.

Duplicate installed providers may be disabled only after replacement verification.
Preserve generated user role sheets and their actual source of truth. Source
coverage and runtime unit tests do not prove a live harness cutover.

### Pocock craft and primitives (2026-08-14)

Adapted selected patterns from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) without copying the 25-skill catalog:

- Writing craft + invocation split live in `skill-standards.md` (leading words, completion criteria, no-ops, positive prompts, user- vs model-invoked composition).
- New adapted primitives: `grilling`, `domain-modeling`, `wait-what`, `wizard`, `prototype`, `codebase-design`.
- New user-invoked router: `ask-dev-loop`. `interview` / `shape` invoke `grilling`; they hint at other user-invoked skills rather than firing them.
- `tdd` provenance completed; `code-review` gained a Spec axis; flagship human docs live in `docs/skills/`.

### Weekly review composition (2026-09-05)

`weekly-review` coordinates board evidence, issue-to-code checks, a frozen
all-author retrospective, operational evidence, and scoped deslop. Report-only
is the default. Existing scoped repair authorization carries to engines; board
writes and deployment actions keep their own boundaries. Code coverage controls
the next review checkpoint, with unresolved work retained separately. Shipshit
`deslop` and upstream `pstack:deslop` remain separate implementations.

### Prepared issue delivery (2026-09-14)

One end-to-end feature per issue/PR by default. `feature-intake` composes the PRD,
plan, readiness gate, and task-creation engines without a separate template.
`prd-quality-gate/references/execution-readiness.md` owns preparation readiness;
`executing-plans/references/delivery-gate.md` owns delivery readiness. Resolve these
through installed skills. Executors implement settled decisions and escalate gaps;
planning does not require complete implementation code. Every implementation needs
independent review from a different contributor lab, current-head evidence, and
green required CI before merge-ready. Done additionally verifies merge and required
deployment. Harnesses own model/effort/capacity configuration. Static validation
proves contract consistency, not guaranteed model behavior or cost savings.

## Known Issues

None currently tracked.

## Key Files

- `.agents/memory/system/skill-standards.md` — authoritative spec doc
- `.agents/memory/system/skill-management.md` — workflow guide
- `scripts/validate-skill-sync.sh` — validation script
- `scripts/generate-catalog-summary.js` — generated catalog facts and documentation blocks
- `scripts/generate-marketplace-bundles.js` — bundle snapshot generation
- `scripts/generate-marketplace-json.js` — marketplace catalog generation
- `catalog.json` — single generated source for counts, bundles, and tracked layout
- `.claude-plugin/marketplace.json` — full marketplace catalog (generated)
- `.github/workflows/generate-bundles.yml` — CI pipeline
