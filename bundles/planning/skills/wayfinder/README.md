# wayfinder

User-invoked. For an effort too big for one session and still foggy: chart a
**map** issue (destination, notes, decisions so far, fog, out of scope) with
decision tickets as child issues, then resolve one ticket per session until the
way is clear. Ticket types are `research`, `prototype`, `grilling` and `task`.
Finished maps feed `/prd prepare`; wayfinder never builds.

Reach it from `ask-dev-loop` when the effort is huge and the decisions are
unmade. It replaces sending foggy work to the ICP roadmap tools.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/wayfinder/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Adapted to house style: Contract block, GitHub-only tracker mechanics (native sub-issues and blocked-by, claim by assignment), a public-repo confirmation, ticket types resolved through this catalog's `research`, `prototype`, `grill-me` and `domain-modeling` skills, and a handoff to `/prd prepare` instead of upstream's spec skill. The upstream tracker-doc section on wayfinding operations is not adopted. Attribution only; not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/wayfinder/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this
table.
