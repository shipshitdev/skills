### Hillclimb

**Execution boundary:** Carry the caller's authorized target, action scope,
report-only mode, host and provider limits into every step. Scheduling, model
selection, account choice and worktree placement remain harness-owned. Publication,
external messages, destructive actions and configuration changes require authority
covering that action. The procedure supplies no new permission.

**You own the metric and the experiment's integrity. Supervise and review; delegate the attempts.** For sustained, iterative improvement of one measurable thing against a target ("hillclimb on X", "make startup 50% faster", "systematically drive down <metric>", "keep trying until <metric> improves by N%"). A one-off fix is Bug fix or Perf issue; this is the loop.

Core discipline: one change, one measurement, keep or revert. Never stack untested changes, and never claim a win from code inspection. The data decides (the corresponding **prove-it-works** principle resource).

1. Ground the workload and architecture before choosing the ruler. Run the **how** skill over the target, name the realistic workload dimensions that can move the result (data size, history, state, concurrency), and select a case that reproduces the user's complaint. If no case reproduces it, fix the repro instead of hillclimbing. Then fix one metric, the direction that counts as better, and a checkable stop predicate that pairs a target with a floor on attempts so a lucky early win can't end the run (the example "at least 50% better than baseline and at least 10 iterations" is this shape). Use the user's numbers when given, otherwise agree them.
2. Build the measurement harness, prove its sensitivity, then freeze it (the corresponding **build-the-lever** principle resource). Run contrasting realistic workloads and confirm the target case reproduces the symptom while easier cases separate as expected. If the ruler cannot distinguish them, revise the workload or metric. Vet the harness with the [benchmark checklist](../references/benchmark-checklist.md) before you freeze it, and make it print its error count and a count of the work done. Once frozen, one repeatable command emits the metric, sampled enough to clear the noise (median of N, not a single run); changing it invalidates every earlier number. Record the baseline metric and a green run of the regression gate (the tests that must keep passing) before any change.
3. Open the decision log via the **show-me-your-work** skill. A `decision.tsv`, one row per attempt: id, hypothesis, change, before, after, delta, tests, verdict (kept or reverted), note. This is the run's memory. Read it before each attempt so the search accumulates instead of circling. Keep it out of the tree (gitignored) so it survives reverts.
4. Ground each hypothesis in the architecture model from step 1, so it names a specific mechanism ("defer X off the boot path because it blocks first paint"), not "try memoizing something". For a perf metric, order hypotheses by the performance mantras in step 2 of the Perf issue playbook (`playbooks/perf-issue.md`). Borrow only their order, not that step's stop rule.
5. Loop, one hypothesis per iteration:
   - Hand the change through provider dispatch using your configured hillclimb descriptor with `isolated-write` and a tight worktree scope; supervise and review the diff rather than typing it (the corresponding **guard-the-context-window** principle resource). When several independent hypotheses are live, fan them to parallel lanes, each in its own worktree so they can't collide (the corresponding **separate-before-serializing-shared-state** principle resource).
   - Measure before and after with the frozen harness, and run the regression gate.
   - Accept only when the metric moves past noise and the gate stays green. Otherwise revert the change in full; a tweak that "might help" does not ride along.
   - One commit per accepted fix, staging only the files you changed (`git add <files>`, never `-A`). Log the row either way, kept or reverted.
   Each iteration ends in a check before the next begins (the corresponding **sequence-verifiable-units** principle resource). If the run is unattended, borrow only the wake mechanism from the Autonomous run playbook (`playbooks/autonomous-run.md`), not its stop rule. This playbook's stop criteria below govern, so a plateau means pivot, not stop.
6. Push past the first plateau. On a stall, several rejects in a row, pivot category, combine near-misses, re-read the source, or try something more radical before concluding the hill is climbed. Correctness and simplicity outrank the number. Revert a win that breaks behavior, and keep a simplification that holds the number (the corresponding **laziness-protocol** principle resource).
7. Stop when the predicate is met, or when the remaining ideas are genuinely marginal and not worth their cost. Don't relax the predicate to declare victory, and don't quit while cheap untried hypotheses remain. If you are stuck, surface it instead of spinning.
8. Run **Opening a PR** with the accepted commits stacked in the order they landed, so the metric's climb reads top to bottom.

**Reply:** the metric and target, baseline to final with the percent delta, iterations run (kept vs reverted), each accepted fix on one line, the `decision.tsv` path, and the best idea you would try next if pushed further.
