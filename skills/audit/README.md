# audit

Run systematic technical quality checks (accessibility, performance, theming, responsive design, implementation integrity) and generate a scored P0–P3 report.

## Upstream

Derived from **[pbakaus/impeccable](https://github.com/pbakaus/impeccable)** (Apache-2.0).

| Field | Value |
|-------|-------|
| Source | [`skill/reference/audit.md`](https://github.com/pbakaus/impeccable/blob/main/skill/reference/audit.md) |
| Forked at | `skill-v4.5.0` |
| Upstream latest | `skill-v4.5.0` |
| Last synced | 2026-10-06 |
| License | Apache-2.0 |

**Local modifications:** removed the hard dependency on the parent `/impeccable` orchestrator skill (not part of this marketplace) and inlined self-contained context gathering and evidence-based integrity checks, including reduced-motion feedback and touch interaction, so the skill runs standalone. Rewrote the description to name this skill as the broad multi-dimension sweep and added a Related section routing deep passes to `accessibility` and `design-consistency-auditor`, so the three do not compete on the same trigger phrasing.

**Checking for upstream changes:** when *Upstream latest* is ahead of *Forked at*, diff [`skill/reference/audit.md`](https://github.com/pbakaus/impeccable/blob/main/skill/reference/audit.md) against tag `skill-v4.5.0`, port anything worth bringing home, then bump `metadata.upstream_version` and `metadata.last_synced` in `SKILL.md` and this table.
