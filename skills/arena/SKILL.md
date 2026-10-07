---
name: arena
description: Runs N parallel candidates at the same task, picks a base, and grafts the best parts of the others into it. Use for arena this, or when one attempt would lock in the wrong shape.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.4"
  tags: "fan-out, bakeoff, design, synthesis"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/arena/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "bakeoff, compare N attempts"
---

# Arena

Fan out N parallel attempts at the same task. Read every candidate end
to end. Pick the strongest as the base. Graft the best ideas from the
others into it. Verify the synthesized result.

Companion to `swarm`, which covers different slices or races and
returns a report. Arena synthesizes one artifact.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A task whose first attempt would lock in the wrong shape
- Optional N and a shared grounding pack

Outputs:

- One synthesized artifact
- A short synthesis note: base, grafts, rejections, dropouts,
  verification

Creates/Modifies:

- Candidate outputs in separate worktrees or
  `.tmp/arena-<slug>/candidate-<n>/`
- The synthesized artifact

External Side Effects:

- None beyond local files unless the caller lands the result

Confirmation Required:

- None for the bakeoff itself

Delegates To:

- `worktree` when candidates need isolated checkouts
- `verification-before-completion` before claiming the result works

## Phases

Open a todo list: Frame, Fan out, Cross-judge, Pick, Graft, Verify.

### A. Frame

State the artifact. Derive a rubric of 3-6 concrete gradeable
criteria. Candidates see the task, not the rubric.

Pick runners across capability tiers and, when possible, different
families. Same-tier N times only when the work is generation-bound.

Assign each candidate its own output path. Shared writes fail
Separate Before Serializing Shared State.

### B. Fan out

Spawn all N subagents in one message. Each produces the artifact and a
rationale naming alternatives it rejected. A dropout proceeds as N-1.

### C. Cross-judge

After candidates complete, spawn one read-only judge on a different
tier or family from the parent. It scores each criterion and
recommends a base.

### D. Pick

Read every candidate end to end. Score criterion by criterion. Compare
against the cross-judge. Prefer the cleaner boundary when two feel
tied.

### E. Graft

Walk each loser once. Port one or two things, by hand, so the result
stays coherent. Record rejections. Wild divergence means Phase A was
under-specified. Reframe and re-run.

### F. Verify

The synthesized artifact holds up under the same scrutiny as any other
output. A miss here is a re-frame or a missed graft, not a paper-over.

## Arena procedure

Read [arena procedure](references/arena-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
