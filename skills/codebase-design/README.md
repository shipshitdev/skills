# codebase-design

Shared vocabulary for designing **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface.

`tech-debt` inventories. This skill is the design language it should speak.

It also carries the read-only **survey modes** that used to be the separate `codebase-advisor` skill: `survey` (handoff plans for other agents), `report` (written analysis for humans), `deepen` (ranked deepening candidates), plus `branch`, `next`, `plan`, `review-plan`, `execute`, `reconcile` and `--issues`. They never edit source code. See `SKILL.md` for the contract and `references/survey.md` for the workflow.

## Upstream

Derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/codebase-design/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d` |
| Last synced | 2026-10-06 |
| License | MIT |

**Local modifications:** Adapted to house style: Contract block, deepening/design-it-twice moved to `references/`, and an explicit split from `tech-debt` (inventory vs language). The survey modes were folded in from `codebase-advisor` on 2026-10-06 (#235); see below. Attribution only — not a sync target.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/engineering/codebase-design/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md) on `main` since commit `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.

## Absorbed upstream: codebase-advisor

`codebase-advisor` was folded into this skill as its survey modes (#235). Its workflow
(Recon, Audit, Vet, Plans, invocation variants) is `references/survey.md`, and that file's
frontmatter keeps the shadcn/improve pin so `scripts/upstream-drift.py` keeps tracking the
path. The read-only hard rules and the operating contract moved into `SKILL.md`; the audit
playbook, plan template, analysis-report guide, closing-the-loop guide and `deepen` survey
are the other files under `references/`. The `npx skills add --skill codebase-advisor` name
no longer installs, and the survey is no longer hidden from model invocation: it is
started only on explicit request, as the contract states. `Bash(gh issue create:*)` is no
longer pre-approved, so `--issues` prompts before creating an issue.

Derived from **[shadcn/improve](https://github.com/shadcn/improve)** (MIT), with the `deepen`
mode derived from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | shadcn/improve (`references/survey.md`) | mattpocock/skills (`references/deepen-survey.md`) |
|-------|----------------|------------------------------|
| Source | [`skills/improve/SKILL.md`](https://github.com/shadcn/improve/blob/main/skills/improve/SKILL.md) | [`skills/engineering/improve-codebase-architecture/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md) |
| Upstream ref | `main` | `main` |
| Synced at commit | `cac56e1ebd3c279aa9153616cfeac7b174ab90f9` | `4588b32ecab9` |
| Last synced | 2026-10-06 | 2026-10-05 |
| License | MIT | MIT |

**Local modifications:** Adapted to house style: strict read-only advisor contract, plan and report modes, and a `deepen` mode (`references/deepen-survey.md`) with hot-spot scoping, the deletion test and an `interview` handoff. The `deepen` survey is attribution only, not a sync target; only the shadcn/improve path is tracked by the drift check.

**Checking for upstream changes:** diff [`skills/improve/SKILL.md`](https://github.com/shadcn/improve/blob/main/skills/improve/SKILL.md) on `main` since commit `cac56e1ebd3c279aa9153616cfeac7b174ab90f9`, port anything worth bringing home into `references/survey.md`, then bump `upstream_commit` and `last_synced` in that file's frontmatter and this table.
