# Manual board scenario matrix

Use these cases to review routing and authorization before integration. Expected
outcomes are design examples, not claims of executed integration tests.

| Scenario | Expected route and result | Write boundary |
|---|---|---|
| GitHub URL, `/configure-board audit`, custom Building/Acceptance/Released columns | configure-board reports actual configuration and mapping; custom names are not preset drift | No writes |
| Jira URL, `/configure-board audit` | configure-board reports filter, columns, and mapped issue statuses through verified capabilities | No issue transitions or configuration writes |
| Missing provider and several possible boards | Resolve missing target; preserve independent inspection | No speculative target or mutation |
| Unknown connected provider | Report verified reads and unsupported operations | No GitHub/Jira helper assumed compatible |
| Missing read permission or an empty permission-filtered result | Report scope and incomplete coverage; do not claim an empty healthy board | No auth changes or integration installation |
| Unknown status meaning | Preserve original ID/label and unknown semantic category | No automatic normalization |
| Optional preset explicitly requested | configure-board prepares exact provider-supported differences and consequences | Approval before writes; no implicit workflow changes |
| Reopened issue with an older merged PR | sync-board keeps work unfinished and explains merge history | No automatic Done recommendation from the older merge |
| Closed, unshipped issue remains In Progress or Review | Count active-lane drift and request disposition review; preserve closure reason | No automatic Done recommendation |
| Cancelled work without a verified merge | Report closed/cancelled separately from shipped | No automatic reopening or closure |
| Missing Priority on a Deferred card | Report the authoritative empty value | Preserve Deferred status |
| Native GitHub Priority empty, stale project Priority populated | Report native value as empty; use its numeric field ID | Approved additive native Priority edit only |
| Jira Priority editable and approved | Verify allowed option ID, edit only Priority, and read back | No transition/resolution/comment fields |
| Jira status correction requested through sync apply | Explain the recommended transition as a separate issue-workflow action | Do not execute it under sync approval |
| Old PR merges inside the activity window | Descending updated-date scan retains it; actual merged date selects it | No early cutoff based on PR creation date |
| Native Priority schema unavailable during configuration audit | Preserve Status/view audit and withhold Priority plan; mark incomplete | Apply blocks before all writes |
| More than one page or nested children/links continue | Follow every relevant cursor; compare counts and disclose remaining gaps | Incomplete evidence cannot authorize a repair batch |
| PR lacks formal closing reference but is already on the board | Report missing formal linkage separately from retained tracking | No invented untracked-work conclusion |
| Review queue contains blocked, approved, and unknown-check items | Return all mapped review items with available evidence | Keep human decisions with the human |
| Archived or removed work absent from current view | Describe exactly what historical membership was inspected | Do not claim complete removed/deleted history |
| Report, schedule, or review mode | Return findings/planning/queue with scope and capability gaps | Zero writes |

## Evaluation limitations

GitHub helper fixtures cover core evidence handling and mutation guards. A live
GitHub snapshot smoke covers a particular board and declared repository scope;
it is not proof of every host, permission model, or future API schema. The reads
are not an atomic transaction. The agent must verify the actual target anew.

The Jira procedure is documentation-reviewed only in this change. These cases
have not been executed against a live Jira tenant. No packaged Jira script,
provider-wide parity, workflow-transition implementation, or successful Jira
write is claimed. A future live evaluation must record its exact connection,
permissions, board/workflow, pagination, and observed behavior.
