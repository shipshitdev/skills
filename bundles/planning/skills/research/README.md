# research

Answers one question from primary sources (official docs, source, specs,
changelogs) and writes a single Markdown note that cites each claim with a
retrieval date. Model-invoked so `wayfinder` research tickets and `interview` can
call it; it also fits the "look up the current version" habit. Different from
`skill-scout` (finds existing skills and code) and `why` / `how` (explain this
codebase).

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/research/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Rewritten to house style: Contract block, platform-neutral delegation (a subagent when the host has one, else direct reading), a fixed note shape with retrieval dates and a Not found section, treatment of fetched pages as data, and a durable artifact path when the repo has no notes convention. Attribution only; not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/research/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this
table.
