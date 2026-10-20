# Jira board configuration

Resolve the explicit Jira site and board ID using an existing connection or
browser. These procedures concern Jira Cloud; verify equivalent capabilities
before applying them to another deployment. There is no packaged Jira normalizer
or live Jira verification in this change.

Read `GET /rest/agile/1.0/board/{boardId}/configuration`. Record filter/subquery,
column order, mapped status IDs, and any constraints. Do not flatten this into a
GitHub-style Status single-select. [Board configuration API](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/).

## Audit

Preserve the actual issue workflow and field ownership. Identify unknown
semantics and unsupported capabilities. Check whether a proposed configuration
would merely change board presentation or alter the issue workflow and shared
settings. A matching label is insufficient evidence of matching behavior.

## Requested configuration

For board creation, verify the approved name, board type, existing filter ID,
destination, and sharing implications before `POST /rest/agile/1.0/board`.
For copy or normalization, use only configuration operations verified in the
available provider/browser; report unsupported operations. Do not invent a
configuration-update endpoint or interpret “move issues to board” as a column
configuration operation. [Board operations](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/).

Editing shared filters, priority schemes, issue status definitions, and workflow
transitions requires a separately scoped task. Approval of a board configuration
plan does not authorize moving or closing the issues it displays. A house preset
is a proposal; preserve existing status IDs and raise incompatible changes for
explicit workflow design rather than applying them mechanically.

Read back the supported configuration changes and report any unapplied part.
Document source/destination and scope in the result. Sources checked 2026-09-05;
this procedure has been reviewed against documentation, not exercised against a
live Jira tenant.
