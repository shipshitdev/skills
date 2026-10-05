# deslop

Strip AI slop from code, product surfaces, and prose. Code slop is the default. `--product` adds the unfinished-app pass. `prose` cuts AI tells from writing. `ui` audits design-system primitives.

The prose catalog lives in `references/prose-slop.md` so other skills can point at it without firing this skill.

## Upstream

Prose-slop rigor is derived from **[Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack)** `unslop` skill (MIT), shipped in [cursor/plugins](https://github.com/cursor/plugins). Code, product, and UI slop are in-house.

| Field | Value |
|-------|-------|
| Source | [`pstack/skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) |
| Upstream ref | `main` |
| Original adaptation commit | `bdf7aa355337` |
| Original adaptation date | 2026-08-26 |
| License | MIT |

**Local modifications:** Renamed the catalog skill to `deslop`; kept the code/product/UI passes, Contract block, and confirmation gate. Recut pstack `unslop` into `prose` mode and `references/prose-slop.md`. No Cursor-only APIs. The original adaptation remains part of this skill; the current integration is tracked below.

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
