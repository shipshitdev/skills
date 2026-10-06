# evaluation

Build evaluation frameworks for agent systems — deterministic validation plus model-judged quality, with attention to token/tool/model performance drivers. Includes an LLM-as-judge mode (direct scoring, pairwise comparison, rubric calibration, bias mitigation) in `references/llm-as-judge.md`.

## Upstream

Derived from **[muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/evaluation/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/evaluation/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `25e1fa79a33f` |
| Last synced | 2026-06-13 |
| License | MIT |

**Local modifications:** Imported 2026-01-20 (this repo's commit ef42a98) from muratcankoylan/Agent-Skills-for-Context-Engineering at v1.0.0-era content. Ported forward 2026-06-13 to upstream HEAD (commit 25e1fa79a33f); local body now tracks upstream v1.2.0 — carried the deterministic-validation concept, Examples 3-4 (deterministic gate + quality-gate dimensions), 8-entry Gotchas, the claim-evaluation-browsecomp-variance ID, and the softened Performance Drivers table (concrete 80%/~10%/~5% -> qualitative Primary/Secondary labels). Reference to a sibling not vendored here (harness-engineering) was stripped. Local divergence: scripts/evaluator.py adopts the upstream citation-detection fix (naive bracket-matching -> academic-citation regex). references/metrics.md is byte-identical to upstream. A 2026-06-13 review-hardening pass (CodeRabbit on PR #21) further diverges scripts/evaluator.py: evaluation_history and samples are now bounded deques (10k/50k) to cap memory growth, and two no-op f-string prefixes were removed (Ruff F541) — candidates to push upstream. To diff: compare the upstream path on main since commit 25e1fa79a33f.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/evaluation/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/evaluation/SKILL.md) on `main` since commit `25e1fa79a33f`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.

## Absorbed upstream: advanced-evaluation

`advanced-evaluation` was folded into this skill as its LLM-as-judge mode (#235). Its
`SKILL.md` body lives in `references/llm-as-judge.md`, and that file's frontmatter keeps
the upstream pin so `scripts/upstream-drift.py` keeps tracking the path. Its former
references and script moved to `references/judge-*.md` and `scripts/llm_judge_example.py`.
The `npx skills add --skill advanced-evaluation` name no longer installs.

| Field | Value |
|-------|-------|
| Source | [`skills/advanced-evaluation/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/advanced-evaluation/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `25e1fa79a33f` |
| Last synced | 2026-06-13 |
| License | MIT |

**Local modifications:** Imported 2026-01-20 (commit ef42a98) at v1.0.0-era content, ported forward 2026-06-13 to upstream commit 25e1fa79a33f (v2.1.0 content: prompt templates, Metric Selection table, worked JSON examples, 10-item Guidelines, 8-entry Gotchas, Scaling section, the claim-advanced-evaluation-position-swap ID, rewritten example script). `references/full-guide.md` was renamed to the pipeline diagram to match upstream; a sibling not vendored here (harness-engineering) was stripped; concrete vendor model names in references were genericized. Folded into this skill 2026-10-06: "When to Activate", "Do not activate" and "Integration" were replaced by this skill's Modes table and routing, and judge-specific guidance that duplicated this skill (self-enhancement bias, LLM-as-judge for scale) was merged into one statement here.

**Checking for upstream changes:** diff [`skills/advanced-evaluation/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/advanced-evaluation/SKILL.md) on `main` since commit `25e1fa79a33f`, port anything worth bringing home into `references/llm-as-judge.md`, then bump `upstream_commit` and `last_synced` in that file's frontmatter and the table above.
