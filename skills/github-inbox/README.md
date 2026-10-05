# github-inbox

Turns scattered GitHub work (review requests, authored PRs with failing checks,
assigned issues, mentions) into a short priority queue, and evaluates a single
inbound issue or PR with `triage <ref>`.

Triage mode verifies the claim before recommending: reproduce a reported bug or
check a PR out in a disposable checkout, search the code for an existing
implementation, and read the `.out-of-scope/` knowledge base for a prior
rejection. It posts nothing until the maintainer approves.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/triage/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Only the `triage <ref>` mode is derived: verify-first, redundancy check, the `.out-of-scope/` knowledge base, the AI disclaimer and the needs-info comment shape, rewritten for house style and a maintainer-approved write gate. Not adopted: the triage label state machine and upstream's durable agent-brief rule (this catalog's `feature-intake` writes execution-ready issues with grounded paths). Attribution only; not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/triage/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this
table.
