# memory-systems

Design layered agent memory architectures — working/short/long-term, entity, and temporal knowledge graphs — that persist state across sessions.

## Upstream

Derived from **[muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/memory-systems/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/memory-systems/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `58b55a8921758d13453b440704fb1b5b208c0b0e` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Imported 2026-01-20 (this repo's commit ef42a98) from muratcankoylan/Agent-Skills-for-Context-Engineering at v1.0.0-era content. Ported forward 2026-06-13 to upstream HEAD (commit 58b55a8921758d13453b440704fb1b5b208c0b0e); local body now tracks upstream v4.1.0 — the largest drift of this cluster — carrying the Production Framework Landscape table (Mem0, Zep/Graphiti, Letta, Cognee, LangMem), named benchmark tables (DMR, LoCoMo, HotPotQA), 8-entry Gotchas, Error Recovery subsection, claim-* IDs, and updated framework-integration examples in references/implementation.md and scripts/memory_store.py. References to siblings not vendored here (filesystem-context, context-compression, bdi-mental-states) were stripped. Local divergence: a Neo4j backend mention in the references Graphiti example was genericized to 'graph database backend'. A 2026-06-13 review-hardening pass (CodeRabbit on PR #21) further diverges scripts/memory_store.py (deterministic SHA-256 embedding seed replacing salted hash(); time_filter now applied to the vector-search filters) and references/implementation.md (same SHA-256 seed fix, local RNG instead of global np.random.seed) — candidates to push upstream. To diff: compare the upstream path on main since commit 58b55a8921758d13453b440704fb1b5b208c0b0e.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/memory-systems/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/memory-systems/SKILL.md) on `main` since commit `58b55a8921758d13453b440704fb1b5b208c0b0e`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
