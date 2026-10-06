---
name: interrogate
description: Runs several independent adversarial reviewers over a diff and synthesizes one verdict without auto-applying fixes. Use to challenge a change or find blind spots.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.3"
  tags: "review, adversarial, multi-reviewer, quality"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/interrogate/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "interrogate, tear this apart, stress test this diff"
---

# Interrogate

Spawn independent reviewers on mixed capability tiers to adversarially
review a change. The signal comes from diverse priors, not assigned
personas. Agreement is high-confidence. Lone findings are worth reading
at lower weight.

The deliverable is a synthesized verdict. Do not auto-apply changes.

Companion to `review-dispatch` (front door), `code-review` (correctness
gate), `grok-review` (one external engine), and `full-code-review`. Use
this skill when the ask is a multi-reviewer adversarial pass.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A diff, branch, or PR to challenge

Outputs:

- A lead verdict bucketed Act on / Consider / Noted / Dismissed, plus
  an agreement map

Creates/Modifies:

- None. Report only.

External Side Effects:

- Read-only git / `gh` to gather the diff

Confirmation Required:

- None

Delegates To:

- Named, not fired: `review-dispatch` when the human wants the catalog
  review front door instead

## Steps

1. **Scope.** Use the pointed files or diff. On a feature branch,
   `git diff <trunk>...HEAD` including the working tree.
2. **Intent.** Write one paragraph of what the code is trying to
   accomplish. Reviewers challenge whether the work achieves that
   intent, not whether the intent is correct. If intent is unclear,
   ask before spawning.
3. **Spawn reviewers.** Launch all reviewers in one message, read-only,
   across at least two capability tiers and, when possible, different
   families. Each gets the same filled template from
   [references/reviewer-prompt.md](references/reviewer-prompt.md), the
   rubric, and the code-quality lens.
4. **Synthesize.** Parse findings. Consensus (2+ independent) is
   highest signal. Deduplicate. Note disagreements.
5. **Lead judgment.** You are a pragmatic lead, not an aggregator.
   Read [references/lead-judgment.md](references/lead-judgment.md).
   Categorize every finding.

## Output format

### Intent

The stated intent paragraph.

### Reviewers

One bullet per reviewer: label, capability tier, finding count. Never
name a concrete model.

### Act On / Consider / Noted / Dismissed

Each finding: description, which reviewers raised it, one-line
rationale.

### Agreement Map

Where reviewers agreed, where they diverged, and what that pattern
means.

## Interrogate procedure

Read [interrogate procedure](references/interrogate-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
