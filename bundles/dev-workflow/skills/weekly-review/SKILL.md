---
name: weekly-review
description: Coordinates a weekly engineering review of board accuracy, recent code changes, operational health and scoped cleanup. Use for a recurring repo health check.
compatibility: Requires repository history and access to the selected board; operational checks depend on existing service connections.
metadata:
  version: "2.2.2"
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
- `full-code-review` for retrospective review using the frozen diff and commit log
- `code-review` for correctness and implementation-versus-acceptance checks
- `deslop` for scoped dry-run findings or authorized cleanup
- `dependency-audit` for dependency checks in audit mode when evidence needs refresh
- `test-runner` for focused verification of authorized repairs

Resolve each engine through the active catalog and resources relative to its
installed directory. Use Shipshit `deslop`; an upstream `pstack:deslop` plugin is
a separate implementation, not an alias. Report missing engines instead of
silently substituting a similarly named skill or installing dependencies.

## Freeze the review scope

Resolve the default branch and pin its fetched tip as END. Review all authors,
including automation accounts. Use the requested branch only when explicitly
selected. Resolve an explicit checkpoint as BASE and verify it is an ancestor of
END. Report rewritten or unavailable history instead of silently resetting it.

For a date window, record absolute start/end and timezone. Identify changes
integrated into the target branch during that interval, including older authored
commits merged during the week. Use integration/merge evidence rather than
author dates alone. Include root-commit content when the window spans repository
creation. Record the commit inventory and endpoints; disclose shallow or missing
history. Inspect individual commit/PR diffs as needed because an aggregate diff
can hide changes later reverted.

Keep uncommitted work and open PRs separate from integrated history. In a monorepo,
list affected applications, shared packages, and downstream consumers. Apply a
package filter without dropping cross-package contracts or claiming whole-repo
coverage. Record any limits before drawing conclusions.

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

Run the `code-review` skill over the frozen changes for correctness and spec
fidelity before the broader retrospective. Run the `full-code-review` skill
with the frozen BASE-to-END diff, changed files,
and COMMIT_LOG. Request its retrospective backlog and cross-commit lens. Preserve
the complete commit inventory, including changes absent from the final diff.
Report per-commit coverage and any omitted hunks or packages.

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
- **Checkpoint:** END only for completely reviewed code scope; retain the previous
  checkpoint and exact remaining scope when review is partial. Required cross-package
  contract and consumer checks are part of that scope; an uninspected required
  consumer prevents advancing the affected checkpoint. Track unresolved
  findings and incomplete board/operational checks separately for the next run.

An empty commit window still permits board and operational review. State no code
changes rather than manufacturing cleanup. Finish report-only runs with the
report. In repair mode, finish the authorized repair/delivery scope or identify
the concrete remaining blocker. A recurring workflow does not itself schedule
an automation.
