# multi-agent-patterns

Design multi-agent architectures (supervisor, swarm, hierarchical) that isolate context across instances without anthropomorphizing role division.

## Upstream

Derived from **[muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/multi-agent-patterns/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/multi-agent-patterns/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `58b55a8921758d13453b440704fb1b5b208c0b0e` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Imported 2026-01-20 (this repo's commit ef42a98) from muratcankoylan/Agent-Skills-for-Context-Engineering at v1.0.0-era content. Ported forward 2026-06-13 to upstream HEAD (commit 58b55a8921758d13453b440704fb1b5b208c0b0e); local body now tracks upstream v2.1.0 — carried the 8-entry Gotchas section, claim-* IDs, the 'Do not activate' routing block, the imperative rewrite of Detailed Topics, and the de-specified qualitative token-multiplier table. References to siblings not vendored here (project-development, hosted-agents, latent-briefing) were stripped; the cross-link to tool-design (vendored) is retained. Local divergence preserved: the 'Dispatching Parallel Agents' section does not exist upstream and was kept intact. references/frameworks.md is byte-identical to upstream. A 2026-06-13 review-hardening pass (CodeRabbit on PR #21) further diverges scripts/coordination.py: the three destructive-inbox call sites now re-queue non-target messages instead of dropping them, and submit_vote validates agent identity, the selection against the topic's options, and the confidence range — candidates to push upstream. To diff: compare the upstream path on main since commit 58b55a8921758d13453b440704fb1b5b208c0b0e; restructured 2026-07-10: long examples moved to references/.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/multi-agent-patterns/SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/multi-agent-patterns/SKILL.md) on `main` since commit `58b55a8921758d13453b440704fb1b5b208c0b0e`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
