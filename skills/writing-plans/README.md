# writing-plans

Resolve a spec into an evidence-backed implementation contract that an executor can implement without choosing missing behavior or architecture.

## Upstream

Derived from **[obra/superpowers](https://github.com/obra/superpowers)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/writing-plans/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `f2cbfbefebbf` |
| Last synced | 2026-06-12 |
| License | MIT |

**Local modifications:** Adapted and maintained here as a platform-neutral planning
engine. Version 2.0.0 replaces complete implementation/test code and fixed 2–5 minute
TDD/commit steps with resolved decisions, repository evidence, exact contracts,
ordered implementation steps and acceptance-to-verification mapping. Reuse the
canonical `prd-quality-gate` readiness contract. Keep requirements and the current
versioned implementation plan on the same issue, with source revision, requirements
fingerprint and blocking freshness checks. Executors escalate missing decisions;
model selection belongs to the harness. Preserve these deliberate differences when
reviewing upstream changes.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/writing-plans/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) on `main` since commit `f2cbfbefebbf`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
