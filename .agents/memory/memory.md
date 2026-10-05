# Skills Repo Memory

last_verified: 2026-08-14

## What This Repo Is

<!-- catalog-summary:start -->
Public skills library at `shipshitdev/skills`. Installable via `npx skills add shipshitdev/skills --skill <name>`. Works with Claude Code, Codex, Cursor, OpenClaw, and Gemini.

Generated catalog: **176 skills · 24 commands · 13 bundles · 189 plugins**.
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
| Skills | 176 | `skills/*/SKILL.md` |
| Commands | 24 | `commands/*.md` |
| Bundles | 13 | `scripts/plugin-categories.json` |
| Plugins | 189 | skills + bundles |
<!-- catalog-counts:end -->

## Architecture Decisions

### Single-Source Skills (2026-02-04)

One `skills/` directory at root. No per-platform copies. Platform-neutral writing: no tool names, imperative style.

### Agent Skills Spec Compliance (2026-04-21)

Follow agentskills.io/specification as base. Claude Code extensions (`when_to_use`, `disable-model-invocation`, `allowed-tools`, etc.) added on top. `version`/`tags` go inside `metadata:` block as strings, not top-level. See `.agents/memory/system/skill-standards.md`.

### Shared release versions (2026-10-03)

All public and repo-maintenance skills, their plugin manifests and generated packages use the
repository release version from `package.json` (2.2.2 at alignment). Vincent
explicitly replaced independent per-skill versions with one shared version.
Run `bun run version:sync` after a repository version change; packaging and
release automation synchronize this automatically. `version:check` verifies
alignment rather than requiring a separate version bump for instruction edits.
Installed metadata updates preserve local behavior and owned customization.

### Listing budget (2026-10-03)

Model-invoked description + `when_to_use` load into every session, and the
catalog's ~54.6k chars overflowed Claude Code's listing so many skills showed no
description. Vincent approved a catalog-wide pass: descriptions ≤ 180 chars
(validator warns > 200), `when_to_use` ≤ 80 (warns > 120) with only new trigger
words — 54.6k → 31.4k chars. The repeated Authorized Scope and Delivery
Readiness paragraphs were shortened in place; skills stay self-contained because
they install individually and cannot share a reference file.

### Overlap merges (2026-10-03)

Vincent approved evidence-based merges after a read-only cluster audit (#168):
`debug` absorbed `execution-debugging` (scoped mode) and `systematic-debugging`
(`references/systematic-debugging.md`, Iron Law verbatim, rolling obra sync
ended); `context-optimization` absorbed `context-fundamentals`
(`references/fundamentals.md` + `scripts/context_manager.py`); `testing-expert`
absorbed `ai-regression-testing` (AI regression mode, `/test regression`);
`structural-review` is the single code-quality rubric and the pstack
thermo-nuclear procedure is `superseded`. Review, interview, `bug`, and `why`
skills stay separate: different side effects, upstream tracking, or pinned tests.

### One release skill (2026-10-03)

Vincent merged `release-pr-gates` and `release-dispatch` into `release`; `/release`
routes straight to it. Rationale: `release-pr-gates` also tagged locally without
the clean-trunk checks or guarded-workflow detection, which side-doored promote
gates such as Genfeed's `release.yml`. `release` now proves checks for the exact
trunk SHA (runs on the SHA plus the producing PR's required checks, because
required checks usually run only on PRs), detects release-please, guarded
`workflow_dispatch`, or tag mode, reads the workflow's declared inputs, and
reports deploy evidence. `deploy-app` no longer triggers on "release". Supersedes the
earlier backlog row that kept the release skills separate (#166).

### Catalog simplification, pair merges (2026-10-05)

Vincent approved the #190 catalog simplification after a read-only overlap audit.
Part 1 (low risk): deleted `grill-me` (alias of `grilling`) and `refactor-dispatch`
(orphan; `/refactor` carries its own mode table). Merged `changelog-generator` into
`release` (`references/notes.md`, written fresh: the Composio upstream had no
LICENSE, so no upstream text remains), `github-address-comments` into `pr-comments`
(`address` mode; `receiving-code-review` no longer claims "addressing PR comments"),
`typescript-refactor` into `typescript-expert` (43 rules under `references/rules/`),
`spec-first` into `prd-dispatch` (`spec` mode), and `fullstack-workspace-init` into
`project-init-orchestrator` (v0 route plus the legacy manual route under
`references/` and `scripts/`). `pr-comments` and `typescript-expert` are pinned
Pstack destinations, so their hashes were re-recorded in `upstream/pstack/mapping.json`.
Removed names no longer install through `npx skills add --skill <name>`; see the
Retired skills table in `docs/skills/catalog-naming.md`. Rejected: keeping thin alias
skills, because they cost a plugin, a directory and a trigger collision each.

### Catalog simplification, routers (2026-10-05)

Part 2 of #190. `commands/agent|deploy|design|prd|skill|test.md` now carry the
full mode-to-engine table (with the aliases the routers held, such as `/test` bare
scope tokens and `/design review`) and name the engines directly, so no command
depends on a model-loadable router (#177 still holds). The six `*-dispatch` routers
became `disable-model-invocation: true` explicit entry points for harnesses without
commands, which removes about 1,440 characters from the model-invoked listing.
`review-dispatch` (13 KB of target resolution, pinned by the validator) and
`ask-dev-loop` stay model-loadable. Rejected: deleting the routers, because that
removes the only portable front door outside Claude Code and breaks
`npx skills add --skill <name>`; a later pass can delete them if that front door is
not wanted. `/prd` gained the `spec` workflow inline (it also lives in `prd-dispatch`).

### Catalog simplification, stack validator (2026-10-05)

Part 3 of #190. `biome-`, `bun-`, `clerk-`, `nextjs-` and `tailwind-validator` merged
into one `stack-validator`: a single `scripts/validate.py` with per-stack check
functions (`--stack biome|bun|clerk|nextjs|tailwind|all`, auto-detected when
omitted), shared `Issue`/`ValidationResult` scaffolding and report, and
`references/<stack>.md` holding each old SKILL body plus its full guide. Existing
checks are unchanged except three deliberate fixes: the Bun check now accepts the
default `bun.lock` (it only knew `bun.lockb`), the Biome config loader no longer
mangles the `$schema` URL while stripping `//` comments (every `biome.json` with a
schema failed as invalid JSON), and Clerk gained the script its old SKILL.md
advertised but never shipped. New fixture tests live in
`skills/stack-validator/tests/`. Rejected: keeping five thin skills with a shared
library, because skills install individually and cannot share a script.

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
`prd-writer`, `prd-quality-gate`, `feature-intake`, `prd-dispatch` (`spec` mode),
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

A lock source may list `ignored_paths`: exact upstream paths or directory prefixes
ending in `/` that are repo-only and never shipped (open-pstack's verify harness and
its symlink). Candidates skip and report them; verify rejects any that are also
archived or mapped. Every other symlink or non-blob upstream object is still rejected.

Sync of 2026-10-05 (issue #188): Pstack advanced to open-pstack 1b03678 and
cursor-pstack 807c031. Take Cursor changes through open-pstack's port up to its
sync marker, and hand-port only later Cursor deltas. Model, routing and effort
defaults, `/loop` and `/goal` autopilot cadence, Cursor-only UI and upstream repo
infrastructure are never adopted. How critique mode is retired. The `correct`
procedure lives in rules-capture, benchmark checklist and prompting in pstack
references, and commit-summary no longer duplicates standup.
The runner is open-pstack's reliability bundle, copied verbatim (portable launcher,
stream sidecars, terminal-failure classification). Grok lanes run with
`--permission-mode auto` (Vincent approved, 2026-10-05) because headless Grok cancels
a turn on any permission prompt. Do not take the reverted Claude write-lane change.

Duplicate installed providers may be disabled only after replacement verification.
Preserve generated user role sheets and their actual source of truth. Source
coverage and runtime unit tests do not prove a live harness cutover.

### Pocock craft and primitives (2026-08-14)

Adapted selected patterns from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) without copying the 25-skill catalog:

- Writing craft + invocation split live in `skill-standards.md` (leading words, completion criteria, no-ops, positive prompts, user- vs model-invoked composition).
- New adapted primitives: `grilling`, `domain-modeling`, `wait-what`, `wizard`, `prototype`, `codebase-design`.
- New user-invoked router: `ask-dev-loop`. `interview` / `shape` invoke `grilling`; they hint at other user-invoked skills rather than firing them.
- `tdd` provenance completed; `code-review` gained a Spec axis; flagship human docs live in `docs/skills/`.

### One session retrospective (2026-10-05)

`retro` (adapted from mattpocock/skills `retro`) is the single session
retrospective. It classifies each friction moment into an environment fix
(navigation pointer, guardrail, reviewer standard, steering cut, no-op, tool
economy, information access) or routes it to `skill-capture` / `rules-capture`.
The Pstack `reflect` procedure moved out of `skill-capture` into
`retro --deep`; its mapping destinations moved with it. `skill-capture` is
capture-only again. `/review retro` stays the commit-window code backlog.

### Pocock gaps (2026-10-05, #189)

Vincent approved rewriting the remaining mattpocock/skills gaps (audit at
upstream `4588b32ecab9`). Landed in order: `writing-for-agents` became
`skill-creator/references/writing-for-agents.md` (only levers skill-standards
lacked); `handoff` is a small user-invoked skill with a phase-boundaries tree in
`ask-dev-loop`; `improve-codebase-architecture` became the `deepen` variant of
`codebase-advisor`; `github-pr-publish` has one PR body template (Summary with a
visual, Evidence, Merge danger, Review guide, Follow-ups) credited to Pocock and
Dex Horthy's `show-me` (humanlayer/skills, MIT). Installed upstream duplicates in
`~/.agents/skills` (handoff, improve-codebase-architecture, writing-for-agents)
are removed by hand after the catalog copies ship.

Second pass: `debug` gained minimise, a tight red-capable loop criterion,
redaction, a human-in-the-loop template, ranked hypotheses shown to the user,
seam-as-finding and the confirmed hypothesis in the commit; `ask-dev-loop`
routes foggy efforts to `interview` + `figure-it-out` (not the ICP roadmap
tools) and adds `retro`, `handoff` and the PR-body route; `domain-modeling` and
`wait-what` accept `GLOSSARY.md` (`CONTEXT.md` stays the default for new repos).

Third pass (new flows): `wayfinder` (user-invoked; a map issue of decision tickets
resolved one per session, hands off to `/prd prepare`, never builds); `github-inbox`
`triage <ref>` mode with an `.out-of-scope/` knowledge base for rejected
enhancements (no label state machine, no durable-brief rule; accepted items go to
`feature-intake`); `interview send` mode (questionnaire for someone else to answer);
a small model-invoked `research` skill. `ask-dev-loop` routes the foggy-effort
case to `wayfinder`.

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
