# GitHub board reconciliation

Resolve the GitHub host, owner, and Project v2 number. Verify the existing
connection can read Projects, repositories, and relevant organization fields.
An authentication failure is a coverage blocker, not evidence of an empty board.

## Read-only helper

Run the packaged script from this skill directory:

```bash
node <skill-dir>/scripts/github-board-report.mjs \
  --owner <owner> --project <number> --repo <owner/repo> --json
```

Options are `--window`, `--stale`, `--horizon`, and `--json`. `--repo` restricts
repository activity checks; board item-state checks still cover the board.
Without `--repo`, activity scope is repositories found in accessible retained
items, not every repository owned by the organization. The script never writes
and does not accept `--apply`; apply is the agent workflow's separate operation.

Defaults map Backlog / In Progress / Human Review / Done / Deferred. For another
workflow, provide existing labels:

```bash
node <skill-dir>/scripts/github-board-report.mjs \
  --owner <owner> --project <number> \
  --status-map '{"inProgress":["Building"],"review":["Acceptance"],"done":["Released"],"deferred":["Parked"]}'
```

Mapping keys are `backlog`, `inProgress`, `review`, `done`, and `deferred`; values
are label arrays. Omitted keys retain defaults. Ambiguous or unknown mappings
prevent a complete interpretation. This option never modifies the workflow.

The collector pages retained active/archived items, project fields, item field
values, children, and closing references. Repository connections avoid Search's
result ceiling. Merged PRs are ordered by descending updated date, so an old PR
merged recently remains reachable. Open issues are ordered by descending creation
date. Each activity scan stops only after observing a date strictly before the
window; actual merged dates select the merge results. An old merge updated
recently is scanned but excluded from recent delivery.

JSON records every connection's counts, historical total, scope, and termination
(`exhausted` or deliberate `window_boundary`). Console output summarizes
collections/pages and shows activity boundaries; it does not print a line for
every nested field read. An out-of-order activity date disables the early stop,
so the scan reads the whole collection; when it exhausts with every ID unique and
the fetched count equal to the reported total, the anomaly is recorded as
`orderAnomalies` without invalidating trust. Otherwise unordered dates, invalid
dates, duplicate or missing activity IDs, and other coverage gaps invalidate
trust. Milestones and focus lists remain paginated.
Archived cards provide membership evidence; their historical lanes and metadata
are not current hygiene targets. Missing content is an inaccessible item, not a
draft. Removed/deleted membership history is unavailable.

Closed, unshipped work left in an active lane appears in `closedInActive` and
participates in the unique drift count. Preserve its closure reason; the finding
asks for disposition review rather than recommending Done.

For schedule, present milestone readiness from the report. For review, also read
the complete set of cards mapped to review through the existing provider or the
paginated board item query; the report's starvation bucket is only a subset of
that queue. Missing check/review data stays unknown.

## Correct field source

Discover native Priority by issue repository organization, even on a board owned
elsewhere. The helper reads organization field schemas and each issue's values.
A native empty value stays empty despite a stale project value. Unavailable native
schema or value prevents fallback and makes coverage incomplete. PR cards use
project fields; they are not native issue-field targets.

The JSON includes `prioritySource`, `priorityField`, `statusField`, project ID,
and item ID. Native field IDs are numeric REST IDs; project field/item IDs are
GraphQL node IDs. Check the source, option ID/name, and current value again before
an approved write. If a project field is absent, request a separately scoped
configuration change rather than creating it during reconciliation.

For approved project Status or project-local Priority values:

```graphql
mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project, itemId: $item, fieldId: $field,
    value: { singleSelectOptionId: $option }
  }) { projectV2Item { id } }
}
```

For an approved native Priority value, use the additive endpoint with a reviewed
payload containing only that field and an existing option name:

```text
POST /repos/{owner}/{repo}/issues/{number}/issue-field-values
X-GitHub-Api-Version: 2026-03-10
{"issue_field_values":[{"field_id":123,"value":"High"}]}
```

Replace the example ID/value with verified, approved values. The field-values PUT
endpoint replaces the full set and is outside this scoped repair. Preserve the
skill's category/batch approval gates and read back each applied change.

## Sources and evidence

GitHub's [Project API guide](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
and [Projects schema](https://docs.github.com/en/graphql/reference/projects)
describe project field values. [Organization field schemas](https://docs.github.com/en/rest/orgs/issue-fields)
and [issue field values](https://docs.github.com/en/rest/issues/issue-field-values)
describe native field IDs and additive updates. Checked 2026-09-05.

The helper's automated fixtures cover pagination, native/project selection,
reopened work, tracking, read-only behavior, and custom status mappings. Live
snapshot evidence covers GitHub only; it does not establish Jira support or a
transactionally consistent board snapshot.
