# tool-design

Design tools agents can use effectively — consolidation, description engineering, response/error-format optimization, and MCP naming discipline.

## Upstream

Derived from **[muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/tool-design/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/tool-design/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `58b55a8921758d13453b440704fb1b5b208c0b0e` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Imported 2026-01-20 (this repo's commit ef42a98) from muratcankoylan/Agent-Skills-for-Context-Engineering at v1.0.0-era content. Ported forward 2026-06-13 to upstream HEAD (commit 58b55a8921758d13453b440704fb1b5b208c0b0e); local body now tracks upstream v2.2.0 — carried the 'Build for Future Models' subsection, the 8-point Tool Audit Checklist, the expanded Gotchas (4 unnamed bullets -> 9 named entries), negative-activation routing, and the rewritten scripts/description_generator.py (Protocol typing, dataclass spec, full evaluator methods). Reference to a sibling not vendored here (project-development) was stripped. Local divergence: vendor-specific case studies, Sandbox references, and concrete model routing were genericized to neutral equivalents. references/best_practices.md is byte-identical to upstream. A 2026-06-13 review-hardening pass (CodeRabbit on PR #21) further diverges scripts/description_generator.py: ErrorMessageGenerator stores templates as dicts and interpolates values before json.dumps, fixing a runtime str.format crash on the literal JSON braces — candidate to push upstream. To diff: compare the upstream path on main since commit 58b55a8921758d13453b440704fb1b5b208c0b0e.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/tool-design/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/tool-design/SKILL.md) on `main` since commit `58b55a8921758d13453b440704fb1b5b208c0b0e`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
