# context-optimization

Apply optimization techniques (compaction, observation masking, KV-cache, partitioning) to extend effective context capacity. Includes a diagnose mode for context degradation (lost-in-middle, poisoning, distraction, confusion, clash) in `references/degradation.md`.

## Upstream

Derived from **[muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/context-optimization/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-optimization/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `58b55a8921758d13453b440704fb1b5b208c0b0e` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Ported to upstream v2.1.0 (2026-05-15 corpus, commit 58b55a8921758d13453b440704fb1b5b208c0b0e) on 2026-06-12 — body and references match upstream. Cross-references to upstream sibling skills not vendored here (context-compression, filesystem-context, project-development, latent-briefing) were removed so routing only names skills present in this marketplace. scripts/compaction.py carries two local hardening fixes over upstream (CodeRabbit-flagged, candidates to push back): ContextBudget now rejects total_limit<=0 and scales the reserved buffer so reservation_limit stays non-negative; calculate_cache_metrics now debits the unhit remainder of a partial cache hit from misses, where upstream counted only the hit fraction and so inflated hit_rate.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/context-optimization/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-optimization/SKILL.md) on `main` since commit `58b55a8921758d13453b440704fb1b5b208c0b0e`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.

## Absorbed upstream: context-degradation

`context-degradation` was folded into this skill as its diagnose mode (#235). Its `SKILL.md`
body lives in `references/degradation.md`, and that file's frontmatter keeps the upstream pin
so `scripts/upstream-drift.py` keeps tracking the path. Its former `references/patterns.md` is
now `references/degradation-patterns.md` and its detector is `scripts/degradation_detector.py`.
The `npx skills add --skill context-degradation` name no longer installs. The earlier
`context-fundamentals` fold (#168) is recorded in the header comment of `references/fundamentals.md`.

| Field | Value |
|-------|-------|
| Source | [`skills/context-degradation/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-degradation/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `58b55a8921758d13453b440704fb1b5b208c0b0e` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Imported 2026-01-20 (commit ef42a98) at v1.0.0-era content, ported forward 2026-06-13 to upstream commit 58b55a8921758d13453b440704fb1b5b208c0b0e (v2.1.0 content: 7-entry Gotchas, claim-* evidence IDs, Examples 3-4, Model-Specific Degradation Thresholds). References to siblings not vendored here (context-compression, filesystem-context) were stripped. `scripts/degradation_detector.py` adopts the upstream numpy-to-stdlib rewrite and carries two hardening fixes (CodeRabbit on PR #21): `detect_lost_in_middle` excludes negative or out-of-range critical indices from the score denominator, and `analyze_context_structure` measures middle-band content by line-span overlap. `references/degradation-patterns.md` is byte-identical to upstream `patterns.md`. Folded into this skill 2026-10-06: "When to Activate", "Do not activate" and "Integration" were replaced by this skill's Modes table and routing; the "Architectural Patterns for Resilience" paragraph and the compaction-trigger guideline duplicated this skill's techniques and were dropped.

**Checking for upstream changes:** diff [`skills/context-degradation/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-degradation/SKILL.md) on `main` since commit `58b55a8921758d13453b440704fb1b5b208c0b0e`, port anything worth bringing home into `references/degradation.md`, then bump `upstream_commit` and `last_synced` in that file's frontmatter and the table above.
