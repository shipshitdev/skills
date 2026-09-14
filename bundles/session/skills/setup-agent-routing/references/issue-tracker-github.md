# Issue Tracker — GitHub Issues and Projects

Seed `docs/agents/issue-tracker.md` using verified repository/project values.
Track issues in `<owner/repository>` and project #`<number>`. Keep status, priority,
assignee and other supported metadata in native tracker fields.

## Canonical Content and Contracts

The issue body contains complete feature requirements and its `Current plan:` line
selects the authoritative implementation-plan comment on the same issue. Resolve
`prd-quality-gate` through the active catalog and read its installed readiness
reference for the content/fingerprint contract. Resolve `executing-plans` and its
installed delivery reference for lifecycle rules. Provisioned workflows also read
`.github/agent-dispatch.md`. Avoid duplicating those contracts in tracker docs.

## Board State

Inspect live field IDs and option names; do not invent them. The common Status
columns are Backlog, In Progress, Human Review, Done and Deferred. Columns show
human-facing location, while `loop:*` labels show activity. Neither a closed issue
nor its board column proves complete delivery.

Use read-only tracker/project inspection to resolve repository identity, issue
comments, membership and fields. Paginate when selecting a complete queue, and
match repository identity as well as issue number. Treat `.github/agent-loop.env`
as validated configuration data, never arbitrary shell source. Apply state writes
only under existing authorization using the shared dispatch/execution owner rules.

## Publication and Relationships

Use structured text fields or UTF-8 body files for multiline issue/PR content;
avoid shell interpolation of tracker text. Re-read before replacement to preserve
concurrent edits and verify saved content after publication.

One issue/PR normally delivers one whole feature, including required API, UI,
wiring, migration, tests and docs. Link children only for independently complete
outcomes under the canonical decomposition rule. Preserve parent acceptance and
integration coverage when children are necessary.

Use the repository's scoped branch convention. Reference the issue in commits and
publish the PR with `Refs #<issue>` plus the current plan link/revision. Handoff is
`review_pending`; do not automatically close the issue at implementation publication.

## Recovery and Completion

Confirm the run ended before explicit claim recovery; timestamps alone do not
release ownership. Follow the shared receipt/claim rules after interrupted runs.

Done requires independent actual implementation review from a different model
provider/lab, green required CI at the final reviewed head, verified merge and
required deployment/migration/smoke evidence. Keep the epic open until every
required outcome and integrated acceptance criterion is satisfied. Reviewer
assignment and self-QA do not replace that review. Closing rejected work is a
separate authorized decision with an explicit reason, not delivery completion.
