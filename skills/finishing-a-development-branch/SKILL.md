---
name: finishing-a-development-branch
description: Finishes an implementation branch through authorized PR publication and verified delivery gates, or preserves/discards it when explicitly requested. Use when coding is complete and the branch needs integration or a delivery status.
metadata:
  version: "2.0.0"
  source: https://github.com/obra/superpowers/blob/main/skills/finishing-a-development-branch/SKILL.md
  upstream_repo: obra/superpowers
  upstream_ref: main
  upstream_commit: f2cbfbefebbf
  last_synced: "2026-06-12"
  license: MIT
  tags: "git, branch, merge, pull-request, workflow, worktree, cleanup"
allowed-tools: Bash(git *) Bash(gh *)
disable-model-invocation: true
---

# Finishing a Development Branch

Carry the authorized delivery path through publication and fresh verification.
Preserve the branch and worktree for review and repair.

## Contract

Inputs:

- Selected branch/worktree, issue, plan, acceptance evidence, and requested action
- Repository merge rules and harness-selected independent reviewer

Outputs:

- PR and delivery state, with evidence and remaining blockers
- Preserved branch, or an explicitly authorized discard result

Creates/Modifies:

- Intended commits, branch pushes, and PR metadata within existing authorization
- Merges only when explicitly authorized and all delivery gates pass

External Side Effects:

- Authorized Git and tracker writes; independent review through the configured lane

Confirmation Required:

- Missing merge authority or any discard/deletion not explicitly authorized
- Existing commit/push/PR authorization does not need repeating

Delegates To:

- `github-pr-publish` for publication
- `executing-plans` for delivery evidence and repair ownership
- Recommend `git-cleanup` for a separately authorized cleanup action

## Publish the Selected Work

1. Read the branch, worktree, default branch, live issue, and current PR state.
   Preserve unrelated changes. Create a scoped named branch when required.
2. Follow the existing authorized path. Do not stop for a four-option menu when
   the user already requested delivery. An explicit keep/report-only request
   performs no writes. If no publication or integration action is authorized,
   report the evidence and available next action.
3. Resolve the repository's verification commands and permitted verification host.
   Run the appropriate checks or collect current CI evidence. Never default to
   a broad local test suite or invent package-manager commands.
4. Commit intended files, push, and create/reuse the authorized PR. Publish with
   pending evidence clearly recorded when external checks/review need a PR first.
   A ready-for-review PR is not a merge-ready verdict.

## Evaluate Delivery

Resolve the installed `executing-plans` skill and read
`references/delivery-gate.md`. Before any merge-ready or Done claim, require the
complete acceptance scope, independent review from a different lab than every
implementation contributor, current-head PASS, resolved findings, and green
required CI. Respect all forge protections and explicit human gates.

Missing review capacity remains blocked. A new implementation commit requires
fresh review and CI. Return concrete defects to the implementation owner and
missing design decisions to the planner. Do not loosen acceptance to finish.

Merge only through the repository's authorized path, bound to the verified head.
Local merging is not a shortcut around remote review or required checks. Report
Done only after the merge and required deployment/migration/enablement/smoke steps
are verified. Partial work does not close the parent epic.

## Preserve or Discard

Keep the branch and worktree after PR creation, merge, or a blocked handoff unless
the user explicitly asks for cleanup. Directory location is not deletion authority.
For an explicit discard, first show the exact branch, unmerged commits, dirty files,
and worktree that would be lost; require confirmation covering that exact scope.
Use the cleanup workflow only after its provenance and loss checks pass.

## Report

Return the PR, implementation head, acceptance evidence, independent reviewer and
reviewed head, CI, merge/deployment state, blockers, and preserved worktree path.
A successful commit or push is not a completed feature.
