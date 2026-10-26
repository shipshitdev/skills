# check

## Upstream

### tstack

The `council` action is adapted from the `council` skill in
**[t3dotgg/tstack](https://github.com/t3dotgg/tstack)** (MIT). The license
ships as `licenses/LICENSE-tstack`.

| Field | Value |
|-------|-------|
| Source | [`skills/council/SKILL.md`](https://github.com/t3dotgg/tstack/blob/main/skills/council/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `7de017b3fc9d` |
| Last synced | 2026-10-26 |
| License | MIT |

**Local modifications:** Seats one delegate per provider CLI detected on the
machine (Claude, Codex, Grok) instead of a fixed three-model panel, runs the
host's own provider as a native subagent, and never names or selects models.
Adds the `/check` diff targets, a JSON output contract, in-session
verification of every finding, a three-round cap, and the rounds table in the
PR description. Owned here; not a sync target.

**Checking for upstream changes:** diff `skills/council/SKILL.md` on `main`
since commit `7de017b3fc9d`, port anything worth bringing home into
[references/council.md](references/council.md), then bump this table.
