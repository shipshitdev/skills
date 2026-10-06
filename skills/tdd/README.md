# tdd

Test-driven development with a red-green-refactor loop. Build or fix one vertical slice at a time, through the public interface. A cheap local path writes the failing check first. An expensive path names why and uses the closest executable proof.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT), with bug-fix rigor adapted from **[Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/tdd/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md) |
| Upstream ref | `main` |
| Original adaptation commit | `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d` |
| Original adaptation date | 2026-08-26 |
| License | MIT |

**Also adapted from:** [`pstack/skills/tdd/SKILL.md`](https://github.com/cursor/plugins/blob/main/pstack/skills/tdd/SKILL.md) at `cursor/plugins` `bdf7aa355337` (2026-08-26). Cheap-path gate, skip-when-impractical, failing-before evidence, and the red-then-green commit story.

**Local modifications:** Adapted to house style: Contract block, vertical-slice and mocking rules, bug-fix path via `debug`, a pointer at `codebase-design` for seam vocabulary, and pstack's cheap-path / prove-it-works discipline. The original adaptation remains part of this skill; the current integration is tracked below.

Use the repository’s pinned Pstack sync workflow to review upstream changes and
verify local adaptations before updating this distribution.

### Current Pstack integration

| Source | Pinned commit | Reviewed |
|---|---|---|
| [Open Pstack](https://github.com/ericlitman/open-pstack) | `1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43` | 2026-10-05 |

Detailed procedures and resources are adapted to canonical skill names and the
harness-owned execution boundary. Existing Shipshit mode and authorization
contracts remain authoritative. Applicable upstream licenses and notices ship
in `licenses/`. Platform-specific adapters are dormant until explicitly set up.
