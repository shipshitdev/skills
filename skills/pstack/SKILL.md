---
name: pstack
description: Playbook orchestrator for verified, unslopped engineering work. Matches a task to a named playbook, applies the principles index, and routes to how, why, architect, arena, swarm, interrogate, tdd, and related skills. Use for pstack, poteto-mode, /pstack, or requests to work in this style.
disable-model-invocation: true
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "56bfd14418fa733e34d98f714f357d28788470e3"
  version: "1.3.0"
  tags: "orchestrator, playbooks, verification, architecture, review"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "pstack, poteto-mode, poteto, work in this style, playbook match, verified run"
---

# pstack

Lauren Tan's poteto-mode, recut for this catalog. Match the task to a playbook.
Copy the playbook steps into the todo list verbatim. Route to the other skills
as the steps fire. Name each principle that shaped a decision.

This is an **execution router** for the task the user selected. Invoke callable
companion engines within that scope. Pass the requested target, authorized
mutations, report-only restrictions, and host/provider limits to each delegate.
Loading a playbook never grants additional authority. Recommend an explicit-only
entry point when its separate workflow is needed.

## Contract

Inputs:

- A non-trivial task: bug, feature, investigation, refactor, perf, shipping, or
  a long unattended run

Outputs:

- A matched playbook, a todo list of its steps, and the playbook's named reply
- Principle citations that trace to a real choice

Creates/Modifies:

- Whatever the matched playbook authorizes

External Side Effects:

- Network, git, and GitHub writes only when the playbook's landing or review
  steps require them

Confirmation Required:

- Irreversible writes: force-push to shared branches, deploys, data deletion,
  customer messages

Delegates To:

- `how`, `why`, `architect`, `arena`, `swarm`, `interrogate`, `tdd`,
  `figure-it-out`, `show-me-your-work`, `blast-radius`, `teach`, `recall`
- `deslop`, `no-comments`, `technical-writing`, `review-dispatch`, `worktree`,
  and `skill-creator` when their steps are authorized
- Recommend `finishing-a-development-branch` or `git-cleanup` for their
  separate explicit workflows

## Installation and Companion Resolution

This is the canonical Shipshit integration of Open Pstack and original Pstack.
Resolve companions through this distribution's active catalog. Installed resources
require neither upstream plugin. Report missing or ambiguous companions before
relying on them. Resolve resources relative to each selected installed skill.

Read [provider dispatch](references/provider-dispatch.md) before launching a
configured role. Read [optional adapters](adapters/README.md) when configuring a
harness; preserve its canonical role sheet and existing generated adapters.
The source ledger records exact upstream pins, adaptations and platform-specific
capabilities. Optional adapters remain dormant until explicitly configured.

For prose, load `references/prose-slop.md` from the selected `deslop` skill.

## Prepared Issue Execution

When implementing a prepared issue, apply the installed `executing-plans` contract
and its `references/delivery-gate.md` across all playbooks. The planner resolves
architecture, scope, contracts, and verification before execution. The executor
implements those decisions and escalates any missing decision; it does not invoke
an architectural investigation to choose a new design on its own authority.
Planning-only requests route through `feature-intake` or `writing-plans` and stop
before implementation. Existing explicit authorization carries across composition.

A complete issue owns the end-to-end outcome. Layer tasks and parallel lanes are
internal work, not evidence that a feature is delivered. Every implementation needs
current independent review from a different implementation lab and green required
CI before merge-ready. A same-provider swarm supplements that review; it cannot
replace it. Keep missing review capacity blocked and record actual evidence.

The prepared issue contract takes precedence over generic playbook defaults that
would re-plan in the executor, require full implementation code in a plan, or add
unrequested fixed-count review panels. Apply verification proportional to the
approved acceptance criteria and risk, retaining every required gate.

## Start

Open a todo list whose first item is reading
[references/principles.md](references/principles.md) in full. Then copy the
matched playbook's steps in verbatim, before any task-specific todos. A step
you skip stays listed with `skip: <reason>`.

## Non-negotiables

- Nontrivial change, architecture decision, or "are we sure?" → the `how` skill.
- About to ask "which approach" or "how should I" → classify first. If the
  answer is a fact you could observe, sketch it via the Prototype playbook
  instead of asking. Reserve the question for a genuine product or preference
  call.
- Any code → name the data shape first (Model the Domain).
- Code crossing a function boundary → the `architect` skill.
- Parallel fan-out → `swarm` for coverage, races, and partitions. `arena` for
  bakeoffs with a base and grafts.
- Contested design → the `interrogate` skill before shipping.
- Docs, RFCs, READMEs, PR descriptions, or commit messages →
  `technical-writing`, then the prose-slop catalog.
- Before review → name `no-comments`.
- PR-status request → the Babysit playbook. Never triggered by merely opening
  a PR.
- Asked to land a green stack → the Shipping playbook. Green is not safe.
- Review-bot comments → triage per
  [references/bugbot-triage.md](references/bugbot-triage.md).
- Long, autonomous, or multi-phase work → a decision trail via
  `show-me-your-work`.
- Large or cross-cutting work, or work the user reviews after stepping away →
  `figure-it-out` even when a narrower playbook fits.

## Capability tiers

Orchestrators speak in tiers. The consuming repo's routing block maps tiers to
models. Never name a concrete model.

- **Fast cheap tier** — fan-out finders, coverage workers, mechanical edits.
- **Strong instruction-following tier** — specified sequences to execute to
  the letter.
- **Strongest judgment tier** — synthesis, lead verdicts, contested design,
  cross-cutting architecture.

Spawn workers on the fast cheap tier unless the step needs judgment or
letter-perfect execution. Review every delegate's diff yourself. Do not pass
through a self-report. For delivery, the independent review must use a different provider/lab from
every implementation contributor. A different tier alone does not qualify.

Give each writer its own worktree or branch. File pointers, not inlined dumps.

## Autonomy

Reversible work proceeds. Pause for irreversible writes. "Don't stop" /
"going to bed" / "run until done" keeps going. No is an acceptable answer.
Decline scope that does not earn its place.

## Writing the reply

Write the reply clean as you draft it.

- Short declarative sentences. One thought per sentence.
- Prefer periods over dashes and mid-sentence colons.
- Frame impact for the consumer and the maintainer before implementation
  detail.
- Never fabricate a link, citation, or transcript reference.
- Apply `references/prose-slop.md` from the selected `deslop` skill directory.

Keep a comment only for a non-obvious *why* the code cannot show.

## Playbooks

Match the task, open the file, copy its steps.

- **Investigation.** Read-only how/why. [playbooks/investigation.md](playbooks/investigation.md)
- **Bug fix.** Reproduce, root-cause, fix with runtime evidence. [playbooks/bug-fix.md](playbooks/bug-fix.md)
- **Perf issue.** One measured slowness. [playbooks/perf-issue.md](playbooks/perf-issue.md)
- **Hillclimb.** Sustained metric loop. [playbooks/hillclimb.md](playbooks/hillclimb.md)
- **Runtime forensics.** Live-instrumentation diagnosis. [playbooks/runtime-forensics.md](playbooks/runtime-forensics.md)
- **Trace forensics.** Captured profile diagnosis. [playbooks/trace-forensics.md](playbooks/trace-forensics.md)
- **Feature.** New behavior from a named data shape. [playbooks/feature.md](playbooks/feature.md)
- **Refactoring.** Behavior-preserving reshape. [playbooks/refactoring.md](playbooks/refactoring.md)
- **Prototype.** Throwaway sketch to decide. [playbooks/prototype.md](playbooks/prototype.md)
- **Visual parity.** Pixel-exact match. [playbooks/visual-parity.md](playbooks/visual-parity.md)
- **Authoring a skill.** [playbooks/authoring-a-skill.md](playbooks/authoring-a-skill.md)
- **Eval.** Blind candidate comparison. [playbooks/eval.md](playbooks/eval.md)
- **Babysit.** Drive a PR to merge-ready. [playbooks/babysit.md](playbooks/babysit.md)
- **Shipping.** Independent verify, then land. [playbooks/shipping.md](playbooks/shipping.md)
- **Autonomous run.** Drive to a predicate. [playbooks/autonomous-run.md](playbooks/autonomous-run.md)
- **Orchestrate.** Standing multi-PR program. [playbooks/orchestrate.md](playbooks/orchestrate.md)
- **Autopilot-full.** Independent PRs to merged. [playbooks/autopilot-full.md](playbooks/autopilot-full.md)
- **Autopilot-stack.** Linear stack the operator lands. [playbooks/autopilot-stack.md](playbooks/autopilot-stack.md)
- **Session pickup.** Resume prior work. [playbooks/session-pickup.md](playbooks/session-pickup.md)
- **Pause safely.** Clean stop. [playbooks/pause-safely.md](playbooks/pause-safely.md)
- **Multi-phase plan.** Checklist, no implementation. [playbooks/multi-phase-plan.md](playbooks/multi-phase-plan.md)
- **Worktree cleanup.** Safety-gated prune. [playbooks/worktree-cleanup.md](playbooks/worktree-cleanup.md)
- **Opening a PR.** End of every other playbook. [playbooks/opening-a-pr.md](playbooks/opening-a-pr.md)

## Automate Me procedure

Read [automate-me procedure](references/automate-me-procedure.md) when creating or updating a personal mode from the user’s working conventions.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.

## Babysit procedure

Read [babysit procedure](references/babysit-procedure.md) when selecting a PR monitoring workflow; the canonical Babysit playbook owns monitoring modes.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.

## Bro procedure

Read [bro procedure](references/bro-procedure.md) when the user asks to restate the previous answer more simply.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.

## Poteto Mode procedure

Read [poteto-mode procedure](references/poteto-mode-procedure.md) when selecting and running an engineering playbook.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
