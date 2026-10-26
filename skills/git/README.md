# git

The `conflicts`, `pr`, and `ci` actions are adapted from upstream Open Pstack; the
`pr` body template also draws on mattpocock/skills.

## Upstream

### Current Pstack integration

| Source | Pinned commit | Reviewed |
|---|---|---|
| [Open Pstack](https://github.com/ericlitman/open-pstack) | `1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43` | 2026-10-05 |

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
`tidy` list. Adds `## Review guide` for large diffs, folds "checks run and on
which host, or `Not run`" into Evidence, and keeps the PR Body Rules (no unproven
test claims, `Closes` only when resolved, `--body-file`). Visual menu and evidence
tiers live in [references/pr-body.md](references/pr-body.md), rewritten in house wording. Attribution
only; not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/pr/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home into
[references/pr.md](references/pr.md), then bump this table.

### tstack

The `babysit` and `modernize` actions and `scripts/pr-wait` are adapted from
the `babysit-pr` and `modernize` skills in
**[t3dotgg/tstack](https://github.com/t3dotgg/tstack)** (MIT). The license
ships as `licenses/LICENSE-tstack`.

| Field | Value |
|-------|-------|
| Source | [`skills/babysit-pr`](https://github.com/t3dotgg/tstack/tree/main/skills/babysit-pr), [`skills/modernize`](https://github.com/t3dotgg/tstack/tree/main/skills/modernize) |
| Upstream ref | `main` |
| Synced at commit | `7de017b3fc9d` |
| Last synced | 2026-10-26 |
| License | MIT |

**Local modifications:** `pr-wait` is copied with three changes: its DIRTY
event asks for a base merge instead of a rebase, a hung `gh` call times out and
retries like other transient failures, and it never reports ready while review
threads beyond the latest 100 are unchecked. Both playbooks update a PR
branch by merging its base and pushing normally, never by rebase and force
push, and ask before any history rewrite. `babysit` defers to a host app's PR
monitor instead of a vendor-specific watcher, posts only replies that dismiss
findings, and hands CI failures and conflicts to `/git ci` and
`/git conflicts`. Owned here; not a sync target.

**Checking for upstream changes:** diff `skills/babysit-pr` and
`skills/modernize` on `main` since commit `7de017b3fc9d`, port anything
worth bringing home into [references/babysit.md](references/babysit.md),
[references/modernize.md](references/modernize.md), or
[scripts/pr-wait](scripts/pr-wait), then bump this table.
