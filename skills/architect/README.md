# architect

Grounds the problem, arenas competing sketches, then implements against the chosen contract.

## Upstream

Derived from **[Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack)** (MIT), shipped in [cursor/plugins](https://github.com/cursor/plugins).

| Field | Value |
|-------|-------|
| Source | [`pstack/skills/architect/SKILL.md`](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/SKILL.md) |
| Upstream ref | `main` |
| Original adaptation commit | `bdf7aa355337` |
| Original adaptation date | 2026-08-26 |
| License | MIT |

**Local modifications:** Recut for this catalog: model-agnostic capability tiers, no Cursor-only APIs, Graphite land paths, or named models, house-style Contract blocks, and routing to existing shipshitdev skills. The original adaptation remains part of this skill; the current integration is tracked below.

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
