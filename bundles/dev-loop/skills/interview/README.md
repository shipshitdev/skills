# interview

User-invoked, repo-grounded discovery interview. Reads the repo first, runs
`grilling` (and `domain-modeling`) on the decisions that cannot be inferred, and
ends in an interview brief for `prd-writer`, `feature-intake` or planning.

`/interview send` is the other direction: when someone else holds the missing
knowledge, it grills only the send (who receives it, what must come back) and
writes a questionnaire for that person.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/productivity/to-questionnaire/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/to-questionnaire/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Only send mode is derived (`references/questionnaire.md`): the grill-the-send interview and the questionnaire shape, rewritten to house style with a durable artifact path. The rest of `interview` is in-house. Attribution only; the upstream skill is not adopted as a separate skill. Attribution only; not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/productivity/to-questionnaire/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/to-questionnaire/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then
bump `metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this
table.
