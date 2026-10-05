# github-pr-publish

## Upstream

### Current Pstack integration

| Source | Pinned commit | Reviewed |
|---|---|---|
| [Open Pstack](https://github.com/ericlitman/open-pstack) | `56bfd14418fa733e34d98f714f357d28788470e3` | 2026-09-05 |

Detailed procedures and resources are adapted to canonical skill names and the
harness-owned execution boundary. Existing Shipshit mode and authorization
contracts remain authoritative. Applicable upstream licenses and notices ship
in `licenses/`. Platform-specific adapters are dormant until explicitly set up.

### Matt Pocock skills

The PR body template (`## Summary` with a visual, `## Evidence` as before and
after, `## Merge danger`) is adapted from the `pr` skill in
**[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/pr/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

The visual menu inside Summary originates in the `show-me` skill by Dex Horthy
([humanlayer/skills](https://github.com/humanlayer/skills), MIT, license checked
2026-10-05); the repository license is MIT and nothing is quoted verbatim.

**Local modifications:** One template replaces the old step 5 list and the
`/pr tidy` list. Adds `## Review guide` for large diffs, folds "checks run and on
which host, or `Not run`" into Evidence, and keeps the PR Body Rules (no unproven
test claims, `Closes` only when resolved, `--body-file`). Visual menu and evidence
tiers live in `references/pr-body.md`, rewritten in house wording. Attribution
only; not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/pr/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this
table.
