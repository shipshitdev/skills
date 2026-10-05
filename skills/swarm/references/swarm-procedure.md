## Distribution boundary

Use the active Shipshit skill catalog and the caller's existing authorization.
The harness owns host, account, model, effort, sandbox, worktree and schedule.
Upstream examples describe mechanisms; they do not grant permission or select
providers. Preserve report-only scope. External messages, publication, installs,
deployment and destructive actions require authorization covering that action.
Read configuration from the harness source of truth; never replace its role map
with an example here. Use only capabilities the active harness actually exposes.

# Swarm

Fan out N parallel workers. They may cover separate slices, race the same brief, or mix both. The parent waits, aggregates, and returns one report.

**Dispatch contract.** Resolve each worker descriptor through `provider-dispatch.md` (resolve the `pstack` skill through the active catalog). The parent starts native and external lanes; workers never route themselves. On Codex, resolve remaining Claude tool names via `codex-tools.md` (resolve the `pstack` skill through the active catalog).

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is total workers, not the number that run at once.
4. Pick the worker descriptor from `swarm workers` in the current harness's pstack model sheet when present. If absent, use an authorized parent-native worker only when the harness policy permits it; otherwise report the unavailable route. For a model race, name each arm's descriptor up front.
5. Give each worker its own writable output when it writes. Use a worktree, branch, or a unique output directory selected by the harness. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Start all N workers in one fan-out phase through provider dispatch. Native lanes use background subagents; external lanes invoke the launcher as background work with retained task/session handles. Never use Claude's foreground Bash path for a long worker. Every writer runs in its assigned worktree or output directory. Isolation comes from those paths, not the provider.

When a worker must start from a non-default branch, check that branch out in the worker's own worktree and name the worktree path in its brief.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note the provider, model, and receipt failure. Never substitute another provider silently.

## Phase C: Aggregate

Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts.

## Phase D: Report

Return one consolidated in-chat report with the table, issue one-liners, gaps or dropouts, and the race rule when used.
