# Jira board reconciliation

Use the user's explicit Jira site and board ID with an existing provider
connection or authenticated browser. This procedure targets Jira Cloud. Check
capabilities and API/version differences before using it with another deployment.
There is no packaged Jira report script or live Jira validation in this change.

## Collect evidence

Read `GET /rest/agile/1.0/board/{boardId}/configuration` for its filter and status
mapping. Collect visible board issues through
`GET /rest/software/1.0/board/{boardId}/issue`, following `nextPageToken` to the
last page. Board results omit inaccessible issues; empty results alone do not
prove the board is empty. Record fetched counts and the permission scope.
[Board API](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/).

Inspect the saved filter and any subquery rather than substituting a project-wide
query. Where additional issue evidence is required, use the connected provider or
`GET /rest/api/3/search/jql` with explicit scope and fields. Follow continuation
tokens, deduplicate issue IDs, and disclose archive exclusions and unavailable
history. Search can lag recent updates; read affected issues directly before
applying changes. [Issue search API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/).

Preserve both status IDs and column labels in the semantic map. A terminal column
is a workflow outcome, not independent shipment evidence. Inspect resolution and
available delivery links. A reopened item remains unfinished even if an older
linked PR merged. Where PR/check integrations are absent, mark those checks
unavailable; do not infer that no PR or failing check exists.

Evaluate the shared checks only against available evidence. Distinguish issues
outside the current filter, missing formal development links, and verified
tracking elsewhere. Enumerate every issue mapped to review. For schedule, use
verified sprint/date information exposed by the connection and disclose missing
planning capabilities; do not convert Jira sprints into GitHub milestones.

## Apply boundary

A Jira board status recommendation is report-only in sync-board. It is not a
project-card field update. A separately authorized issue-workflow action must
review any transition and its consequences. Do not call a board “move issue”
operation as a shortcut around that boundary.

For approved Priority edits, first read
`GET /rest/api/3/issue/{key}/editmeta`. Verify that Priority is editable and select
an allowed ID. Re-read the issue, then send only the approved Priority field to
`PUT /rest/api/3/issue/{key}` and read it back. Example payload:

```json
{"fields":{"priority":{"id":"<verified-approved-id>"}}}
```

Do not add `transition`, resolution, comments, or other fields. If metadata does
not permit the edit, return the concrete blocked action. Do not bypass screen or
workflow restrictions. [Issue edit and transition APIs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/).

Sources checked 2026-09-05. These instructions and worked scenarios establish a
reviewable contract; they are not evidence that a particular Jira connection,
permission set, or workflow has passed a live audit.
