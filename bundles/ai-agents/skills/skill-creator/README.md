# skill-creator

Guide for authoring effective Agent Skills — structure, description discipline, and progressive disclosure.

## Upstream

Derived from **[anthropics/skills](https://github.com/anthropics/skills)** (Apache-2.0).

| Field | Value |
|-------|-------|
| Source | [`skills/skill-creator/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `b0cbd3df1533` |
| Last synced | 2026-06-12 |
| License | Apache-2.0 |

**Local modifications:** Promoted to adapted. Adds a house writing-craft section (invocation split, leading words, completion criteria, no-ops, positive prompts, Contract blocks, provenance) that points at this catalog's skill-standards. Anthropic packaging scripts remain; authoring for this library must pass house standards.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/skill-creator/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) on `main` since commit `b0cbd3df1533`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.

### Matt Pocock skills

`references/writing-for-agents.md` is adapted from `writing-for-agents` in **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT) at commit `4588b32ecab9` (2026-10-05). Only the levers the catalog's skill-standards lacked were kept (two loads, co-location, sprawl, split-by-sequence, environment-as-cache, sediment); the rest of the upstream document duplicates "Writing craft" there. Rewritten in house style; attribution only, not a sync target.
