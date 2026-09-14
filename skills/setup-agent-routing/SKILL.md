---
name: setup-agent-routing
description: Sets up an `## Agent skills` routing block in CLAUDE.md/AGENTS.md plus docs/agents/ so the dev-loop skills (executing-plans, feature-intake, prd-writer, qa-reviewer) know this repo's GitHub issue tracker, kanban label vocabulary, and domain doc layout. Run once per repo before first use of the loop, or when those skills appear to lack tracker, label, or domain context.
license: MIT
metadata:
  version: "2.0.0"
  tags: "setup, routing, github, labels, dev-loop"
  author: Ship Shit Dev
allowed-tools: Bash(git remote*) Bash(gh label list*) Bash(gh project list*) Bash(gh repo view*)
---

# Setup Agent Routing

Configure one thin routing index and consumer tracker/domain documentation for
the prepared issue workflow. Reuse the canonical readiness and delivery contracts;
setup records where to find them, not another execution procedure.

## Authorized Scope

Preserve the user's target and existing write authorization. Read-only/report-only
requests stay read-only. Existing approval for this setup covers the requested local
files; ask only for consequential missing choices or expanded authority. Model,
effort, account, checkout and provider policy remain harness-owned.

## Contract

Inputs:

- Target repository, existing agent instructions and `docs/agents/` layout.
- Live tracker/project fields, labels, and user-approved overrides.

Outputs:

- One `## Agent skills` index and populated tracker, triage and domain documents.
- Present/missing state, canonical resource locations and unresolved setup blockers.

Creates/Modifies:

- The existing `CLAUDE.md` or `AGENTS.md` routing block, updated in place.
- `docs/agents/{issue-tracker,triage-labels,domain}.md`, preserving unrelated content.

External Side Effects:

- Read-only GitHub inspection and authorized local documentation writes.
- No issue labels, board changes, workflows, model configuration or dispatch writes.

Confirmation Required:

- Ask only for a missing target/authority or consequential choice not settled by
  session context or repository convention. Prepare drafts before any required
  approval; do not ask again between writes already covered by that approval.

Delegates To:

- File pointer: `executing-plans` and its installed delivery reference define execution.
- File pointer: `prd-quality-gate` and its installed readiness reference define preparation.
- Recommend `domain-modeling` to maintain the discovered domain layout separately.

## 1. Inspect Existing Context

Read remote identity, current agent instructions, `docs/agents/`, domain documents,
labels, and the configured project. Inspect live board fields and paginate queries
when complete inventory is needed. Preserve existing vocabulary and use native
priority where configured; do not invent board IDs or duplicate fields.

Resolve `executing-plans` and `prd-quality-gate` through the active skill catalog.
Resolve references relative to each selected installed directory, never an assumed
source checkout. When provisioned, `.github/agent-dispatch.md` and its setup-pinned
`.github/agent-skills/` resources own workflow dispatch. Missing required resources
are setup blockers, not permission to seed a weaker fallback contract.

## 2. Settle Missing Setup Choices

Use existing evidence for repository/project, label strings, domain layout and
instruction-file selection. Prefer the established instruction file; if both exist,
follow their documented canonical/generated relationship. If neither exists and
repository convention is absent, ask which one to create. Ask only unresolved
consequential questions; do not poll the user for known decisions.

Use the [triage seed](references/triage-labels.md) for the label roles. It records
`dispatch:plan` as the OpenAI planner workflow, with models/effort selected by the
harness. Execution gates require a current prepared contract and explicit authority;
AFK is earned by readiness, not implied by a label. Identify human-only and
planner-owned blockers separately.

## 3. Write a Thin Index and Consumer Docs

Within existing authorization, update the `## Agent skills` block in place and seed
only missing or stale sections of `docs/agents/`. Preserve user overrides and other
content. Use the reference templates as location/vocabulary guidance; do not copy
execution steps or complete issue templates into multiple documents.

```markdown
## Agent skills

### Issue tracker

GitHub Issues on <owner/repository>, project #<number>.
See docs/agents/issue-tracker.md for verified tracker configuration.

### Prepared delivery

Resolve executing-plans and prd-quality-gate through the active skill catalog;
read their installed delivery/readiness references. For provisioned workflows,
read .github/agent-dispatch.md and use its pinned skill resources.
See docs/agents/triage-labels.md for local label roles and delivery-state mapping.

### Domain docs

<Single-context or multi-context layout>. See docs/agents/domain.md.
```

Ensure the seeded docs preserve these invariants: confirm the run ended before
explicit claim recovery; implementation PRs use `Refs #<issue>` and hand off as
`review_pending`; Done requires independent actual review from a different model
provider/lab, green required CI at the final head, verified merge and required
deployment evidence. Keep the epic open until its integrated acceptance is complete.
A review request, self-QA or reviewer assignment cannot substitute for review.

## 4. Verify and Report

Read the resulting index and referenced docs. Check that resource resolution works
in the target installation, the index is not duplicated, and no generated seed
contradicts the shared contracts. Report changed paths, missing resources, and
unresolved setup choices. Setup completion does not claim a live dispatch or review
route has been exercised; verification of those routes requires actual evidence.

## Reference Seeds

- [Issue tracker](references/issue-tracker-github.md) — tracker identity and native fields.
- [Triage labels](references/triage-labels.md) — dispatch, ownership and delivery state.
- [Domain layout](references/domain.md) — single- or multi-context glossary layout.
