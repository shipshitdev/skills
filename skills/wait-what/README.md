# wait-what

Fire this the moment a message does not land. The agent re-pitches it with the missing context, in plain English, using the repo's glossary vocabulary (`CONTEXT.md`, or `GLOSSARY.md` when the repo uses it).

It works after the fact. `interview` plus `domain-modeling` are the upfront cure: a shared language agreed early is what stops the jargon arriving at all.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/productivity/wait-what/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Adapted to house style: Contract block, explicit re-pitch steps, a pointer at `domain-modeling` when the confusion is a glossary conflict, and glossary lookup that accepts `GLOSSARY.md` and follows a map file to the right context (2026-10-05 re-sync). Attribution only — not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/productivity/wait-what/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) on `main` since commit `4588b32ecab9`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
