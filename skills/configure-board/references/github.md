# GitHub board configuration

Resolve the actual host, owner, and Project v2 number. Verify existing project
access. Paginate project fields, views, and relevant item ownership before
claiming the configuration inventory is complete.

## Inspect before choosing a target

Use the available project connection or GraphQL reads to inventory the actual
Status options, field IDs, views, and Priority source. GitHub project Status is
project-scoped. Native Priority belongs to issue repository organizations; its
schema is not governed by this board's configuration task.

The packaged helper is `scripts/setup-github-board.mjs`. Its defaults propose
the house preset. Use that proposal only when the user selected the preset, or
supply explicit desired options after inspecting the existing workflow:

```bash
node <skill-dir>/scripts/setup-github-board.mjs \
  --owner <owner> --project <number> \
  --status "Backlog,Building,Acceptance,Released,Parked" \
  --priority "P0,P1,P2,P3"
```

Without `--apply` the helper writes nothing. A changed proposal is not itself
proof that an unfamiliar configuration is defective. Native field discovery
covers the board owner and represented issue repository owners. Existing native
Priority causes project Priority normalization to be skipped. Inaccessible or
ambiguous discovery withholds the Priority plan and marks the read-only audit
incomplete while preserving available Status/view evidence. Apply fails before
any mutation while that ownership remains unresolved.

## Approved changes

After approving the displayed plan, rerun with the same target/options and
`--apply`. `--exact` can remove options and clear associated values; it requires
approval of those consequences. Preserve unknown options by default and retain
IDs for surviving options. `--all-open` processes the explicitly requested owner
scope. `--include-closed` requires explicit scope including closed boards.

For a requested copy, resolve source, destination, and title before executing:

```bash
gh project copy <source-number> \
  --source-owner <source-owner> --target-owner <target-owner> \
  --title "<approved-title>" --format json
```

Do not silently choose a hard-coded reference board. A copied board can retain
an obsolete project Priority field; leave its migration as a separately reviewed
change rather than deleting fields during reconciliation.

The helper can configure supported project fields. If a desired board layout or
view cannot be created through the available API, use an already authorized,
available browser capability or report that operation as unsupported. Do not
claim a successful layout change from successful field mutations alone.

## Sources and verification

The [Projects API guide](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
documents project field operations. [Organization issue fields](https://docs.github.com/en/rest/orgs/issue-fields)
document native field ownership and schema. Checked 2026-09-05.

Deterministic helper fixtures check report-only behavior, native Priority guards,
project-local configuration, and linked organization ownership. They do not
replace permission and read-back checks on the actual destination board.
