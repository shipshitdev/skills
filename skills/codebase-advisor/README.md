# codebase-advisor

Read-only senior advisor: surveys a codebase and hands back implementation plans
for another agent, a written analysis for humans, or (`deepen`) the refactors
that turn shallow modules into deep ones.

## Upstream

Derived from **[shadcn/improve](https://github.com/shadcn/improve)** (MIT), with
the `deepen` variant derived from
**[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | shadcn/improve | mattpocock/skills (`deepen`) |
|-------|----------------|------------------------------|
| Source | [`skills/improve/SKILL.md`](https://github.com/shadcn/improve/blob/main/skills/improve/SKILL.md) | [`skills/engineering/improve-codebase-architecture/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md) |
| Upstream ref | `main` | `main` |
| Synced at commit | `5428507e7116` | `4588b32ecab9` |
| Last synced | 2026-06-12 | 2026-10-05 |
| License | MIT | MIT |

**Local modifications:** Adapted to house style: strict read-only advisor
contract, plan and report variants, and a `deepen` variant
(`references/deepen.md`) with hot-spot scoping, the deletion test and an
`interview` handoff. Attribution only — not a sync target.

**Checking for upstream changes:** diff each source above on `main` since its
synced commit, port anything worth bringing home, then bump
`metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` (for
shadcn/improve) and this table.
