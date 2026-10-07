---
name: weekly-review
description: Coordinates a weekly engineering review of board accuracy, recent code changes, operational health and scoped cleanup. Use for a recurring repo health check.
argument-hint: "[7d|since <SHA>] [--report-only|--fix]"
compatibility: Requires repository history and access to the selected board; operational checks depend on existing service connections.
metadata:
  version: "2.2.4"
  tags: "review, weekly, maintenance, boards, retrospective"
  author: Ship Shit Dev
---

# Weekly Review

Turn a review period into an evidence-backed maintenance report and, when
requested, verified repairs. Reuse the review and cleanup engines. Keep provider
procedures and review rubrics in their owning skills.

## Contract

Inputs:

- Repository or monorepo, board URL/provider, and optional package scope
- A window such as `7d` (default), explicit dates with timezone, or `since <SHA>`
- Optional previous review checkpoint and explicitly authorized repair scope
- Report-only by default; `--fix` authorizes code repairs for confirmed findings
  within the reviewed scope; `--report-only` overrides earlier repair authority

Outputs:

- One report of shipped, broken, drifted, blocked, repaired, and next priorities
- Evidence and coverage per repository, issue, package, and operational check
- Reviewed commit endpoints and a proposed next checkpoint, with unfinished work

Creates/Modifies:

- Nothing in report-only mode; return the report and checkpoint in the response
- In repair mode: scoped source/test edits and verification artifacts; publish
  repair PRs according to the repository's existing delivery policy

External Side Effects:

- Reads repository, board, CI, deployment, and available monitoring evidence
- Board edits, issue filing/closure, comments, merges, deployments, installations,
  and scheduling require their own explicit scope; `--fix` grants none of these

Confirmation Required:

- Only for missing or expanded authority; preserve existing explicit approval
  for the same target/actions and forward restrictions to every delegate
- Review requests and findings are not permission to modify production

Delegates To:

- `board-sync` for board reconciliation and approved supported field corrections
- `full-code-review` for the shared merged-history retrospective and cross-commit lens
- `code-review` for correctness and implementation-versus-acceptance checks
- `deslop` for scoped dry-run findings or authorized cleanup
- `dependency-audit` for dependency checks in audit mode when evidence needs refresh
- `test-runner` for focused verification of authorized repairs

Resolve each engine through the active catalog and resources relative to its
installed directory. Use Shipshit `deslop`; an upstream `pstack:deslop` plugin is
a separate implementation, not an alias. Report missing engines instead of
silently substituting a similarly named skill or installing dependencies.

## Freeze the review scope

Read [Shared merged history](references/merged-history.md), which owns the
all-author integration inventory, frozen BASE/END, and code-history review also
used by `standup all … audit`. Follow its freeze/inventory steps for the selected
window and package scope, retaining complete introduced-commit history and the
union of changed files/hunks. Use its audit mode for code review; its report-only
boundary applies even when this weekly invocation separately authorizes repairs.

## Audit work and implementation

Run the `board-sync` skill in report mode for the selected board and scope.
Preserve its status semantics and incomplete-coverage findings. Audit every
current in-scope issue, including backlog and deferred work; report archived
history coverage separately. Inventory issues missing from the board as well as
cards missing repository linkage.

For each issue, compare the stated problem and acceptance criteria with current
code, relevant tests, linked PRs, and deployment evidence where shipment matters.
Run the `code-review` skill for a targeted diff/spec comparison when useful.
Distinguish implemented, partial, still valid, superseded/duplicate, and unclear.
Keep stale issue wording separate from a real code defect. Absence of a patch or
a closed issue does not establish implementation or deployment.

Return an issue coverage table with evidence and proposed disposition. Mark
uninspected issues explicitly; a sample cannot support an all-issues verdict.
Recommend closure or reprioritization only when evidence supports it.

## Review the period

Complete the shared merged-history audit with the same frozen scope. Reuse its
individual/combined correctness and cross-commit findings, PR/review history,
exact-SHA CI/deployment evidence, and coverage ledger. Keep the board's targeted
issue/spec comparisons separate; avoid reviewing the same frozen changes twice.

Combine new findings with the issue audit. Check existing issues and open PRs
before proposing another repair. Trace findings to files, commits, and affected
behavior. Keep a missing spec visible instead of inventing requirements.

Read existing CI, security/dependency alerts, deployment, and monitoring reports
for the same scope. Check recurring errors, failed jobs, flaky checks, rollbacks,
and integrated changes awaiting deployment. Run `dependency-audit` in audit mode
only when relevant evidence is stale or absent and execution is available on an
allowed host. Report each unavailable source as unavailable, not healthy.
Reserve a full security or architecture audit for evidence that warrants it.

## Repair and deslop

Run the `deslop` skill in dry-run mode over the explicitly frozen changed files
and hunks. Pass that scope directly; its default branch-diff calculation may be
empty after changes have merged. Review-only runs stop at findings.

With repair authority, address confirmed defects before cleanup. Retain existing
behavior during deslop; preserve meaningful checks, technical language, and
product intent. Apply findings to current code in an isolated scoped branch,
rechecking evidence when the branch has advanced. A weekly request does not
authorize a whole-tree rewrite.

Run the `test-runner` skill for affected verification, preserving host restrictions
and the authorized repair scope. Satisfy repository-required local checks and
review gates before publication. If the allowed verification host is unavailable,
keep the repair unverified; do not substitute CI for required local checks.
Follow the repository's policy for any draft PR. Use fresh CI and required review
for a separately authorized merge. Report completed actions separately from
planned actions. Failed checks remain unresolved findings.

Re-read affected board evidence after repairs. Apply only separately authorized,
provider-supported corrections through `board-sync`. Issue closure and Jira
transitions remain distinct actions. Do not normalize board configuration merely
to make the audit pass.

## Close the review

Deliver one concise report with evidence links:

- **Scope and coverage:** repository/board, window, BASE/END, commit and issue
  counts, packages, sources, and completed/unavailable/uninspected checks
- **Shipped:** verified delivery; list merged-but-not-deployed work separately
- **Broken, drifted, blocked:** prioritized findings with existing issue/PR links,
  impact, evidence, and the proposed next action
- **Repaired:** exact changes, verification, PRs, and remaining delivery gates
- **Next priorities:** the three highest-value actions, or fewer when justified
- **Checkpoint:** apply the shared merged-history code-coverage gate and return
  its scope-qualified checkpoint/remainder without saving it. Track unresolved
  findings and incomplete board/operational checks separately for the next run.

An empty commit window still permits board and operational review. State no code
changes rather than manufacturing cleanup. Finish report-only runs with the
report. In repair mode, finish the authorized repair/delivery scope or identify
the concrete remaining blocker. A recurring workflow does not itself schedule
an automation.
