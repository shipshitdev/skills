# handoff

User-invoked. Writes one handoff file so a fresh agent session can continue the
work: goal, verified state, decisions with reasons, open questions, pointers to
existing artifacts, suggested skills and the first move. Files land under
`~/.codex/artifacts/handoffs/`.

It is the narrow branch of the phase-boundaries tree in `ask-dev-loop`: reach for
it only when a new harness, a new directory or repository, a colleague, or a
forked side task needs the context. Receiving side: `recall` or the `pstack`
Session pickup.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/productivity/handoff/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Adapted to house style: Contract block, a fixed section
order with verified/unverified marking, durable artifact path instead of the OS
temp directory, `<REDACTED>` convention, and the receiving side named. Attribution
only; not a sync target. The upstream `claude-handoff` skill is not adopted: it
launches a background session outside the account launchers.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/productivity/handoff/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this
table.
