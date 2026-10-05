# retro

Session retrospective. Reads one agent session, marks every friction moment, and
proposes the environment change that prevents it next time: a navigation
pointer, a wired guardrail, a reviewer standard, a steering cut, a tool or
access fix, a skill edit, or a captured preference. It proposes only; nothing
changes until you pick candidates.

`--deep` runs three read-only reviewer lenses (judgment, tooling, divergent) and
a synthesizer over the same record. This is the former Pstack `reflect`
procedure, folded in so the catalog has one session retrospective.

Not the same as `/review retro`, which turns a commit window into a code
backlog.

## Upstream

### Current Pstack integration

| Source | Pinned commit | Reviewed |
|---|---|---|
| [Open Pstack](https://github.com/ericlitman/open-pstack) | `1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43` | 2026-10-05 |

`references/` holds the adapted Pstack `reflect` procedure (deep mode) and its
reviewer templates, tracked in `upstream/pstack/mapping.json`. Applicable
upstream licenses and notices ship in `licenses/`.

### Matt Pocock skills

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/retro/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Adapted to house style: Contract block, completion
criteria per step, skill and preference categories routed to `skill-capture`
and `rules-capture`, a generic reviewer standards file instead of
`CODING_STANDARDS.md`, inline writing rules instead of a `writing-for-agents`
dependency, a guardrail proof before wiring, and `--deep` mode from the Pstack
`reflect` procedure. Attribution only — not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/retro/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and
this table.
