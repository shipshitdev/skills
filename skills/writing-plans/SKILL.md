---
name: writing-plans
description: "Resolves implementation decisions from researched requirements into an exact, current execution plan on the same issue. Use before handing coding to an executor that must escalate missing decisions."
metadata:
  version: "2.1.0"
  source: https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md
  upstream_repo: obra/superpowers
  upstream_ref: main
  upstream_commit: f2cbfbefebbf
  last_synced: "2026-06-12"
  license: MIT
  tags: "planning, implementation-plan, tasks, tdd, dry, yagni, decomposition"
when_to_use: "write a plan, create implementation plan, plan this feature, break this into tasks, plan before coding, spec to tasks"
---

# Writing Plans

Settle every implementation decision before handoff. The executor writes the code;
the planner specifies the contracts, steps, patterns, and proof that remove the
need to choose an approach. Keep production code and complete test bodies out of
the plan; include signatures, data examples or concise algorithms only when needed
to settle ambiguity.

## Contract

Inputs:

- Requirements, target repository, current issue/document, and scope constraints.
- Harness-selected planner and authorized publication scope.

Outputs:

- One current implementation plan bound to requirements and an inspected revision.
- Resolved decisions, exact paths/symbols, ordered steps, verification mapping, and
  blocking readiness result.

Creates/Modifies:

- The authorized `## Implementation Plan` comment on the requirements issue, or
  the plan section in the single canonical local document.
- No implementation files and no autonomous executor dispatch.

External Side Effects:

- Repository/tracker reads and authorized plan publication.

Confirmation Required:

- Ask only for missing authority or consequential intent. Authorization to prepare
  or plan this issue already covers that scope; skip repeated approval prompts.
  Return a draft to a coordinating engine when it owns publication.

Delegates To:

- `prd-quality-gate` for the canonical plan template and execution-readiness check.

## Research and Decide

1. Read live requirements and relevant comments, repository instructions and
   architecture, current revision, and existing implementation. Load the canonical
   execution-readiness reference through `prd-quality-gate`.
2. Map existing paths/symbols and at least three nearby patterns; if fewer exist,
   document the searched scope and available evidence. Label proposed files and
   symbols explicitly. Follow the repository architecture without speculative
   restructuring. Include relevant source evidence, not brittle line numbers alone.
3. Resolve architecture, interfaces, data shapes, validation, authorization,
   concurrency, errors, compatibility, UI states, migration and rollout behavior
   wherever applicable. Specify names and concrete rules; avoid phrases such as
   "handle appropriately", "choose a library", or "follow best practices".
4. Keep the complete feature in one plan and issue. Technical layers form steps,
   not separate completion tickets. Apply the shared independent-outcome rule only
   if a split is necessary; retain parent acceptance and integration obligations.
5. Make each step identify exact files/symbols, the change, selected pattern and
   decision references, prerequisites, and finish condition. Choose logical step
   size instead of fixed minute limits or a commit after every tiny edit.
   Require Touch (all permitted paths, including generated outputs), Pattern
   (existing path/symbol, decision ID, or None with a reason), Check (exact command,
   cwd, and expected result), and Stop if (condition requiring planner escalation)
   on every step, using the canonical template. The executor edits only Touch paths.
6. Map every acceptance ID to decisions, steps, and concrete checks. Inspect the
   command definitions and CI configuration; record cwd, permitted execution host,
   environment/fixtures and expected result. Proposed new tests need exact paths,
   behaviors/fixtures and invocation through a verified runner, not full test code.
7. Record a reproducible base commit, requirements fingerprint and plan revision.
   Compute the fingerprint with the `executing-plans` skill's
   `scripts/plan-header.mjs digest` command on the saved issue body. Pass
   `plan-header.mjs check` against the current head before declaring READY.
   Resolve all planner-owned unknowns. User-owned intent or unavailable prerequisites
   remain explicit blockers, never choices delegated to a smaller executor.

## Review, Store, and Handoff

Run the `prd-quality-gate` skill in blocking `execution-readiness` mode. Repair
coverage gaps, inconsistent names/contracts, ambiguous choices and unverified
command assumptions. Return a verdict with evidence, not a heading-only check.

Publish within existing authorization or return the draft to the coordinator.
Keep requirements in the issue body and one current `## Implementation Plan`
comment on that issue. Follow the shared metadata and freshness protocol. Link the
current comment and explicitly supersede old plans; never split an ambiguous plan
across unlabeled comments. If it exceeds tracker limits, reduce duplication or
split genuinely independent outcomes instead of truncating decisions.

Report the issue/plan link, inspected revision, readiness verdict and blockers.
Do not select model/effort/provider, invent dispatch labels, or ask the user to
choose an execution strategy: those belong to the harness and authorized workflow.
Before execution, require live freshness validation. Any implementation gap goes
back to the planner; the executor cannot revise decisions or acceptance criteria.
