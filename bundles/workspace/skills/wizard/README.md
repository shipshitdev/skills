# wizard

Generate an interactive bash script that walks a human through steps only they can perform: third-party dashboards, credentials, CI secrets, one-off migrations.

The library above the `STAGES` marker in `scripts/template.sh` is identical in every wizard. Author stages below the marker.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/wizard/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Adapted to house style: Contract block, `scripts/template.sh` path (house layout), platform-neutral imperative prose. Template library above `STAGES` kept byte-compatible with upstream so generated wizards share one UX. Attribution only — not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/engineering/wizard/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md) on `main` since commit `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
