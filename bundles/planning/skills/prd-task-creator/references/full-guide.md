# Publishing Guide

## Shared Content

Resolve `prd-quality-gate` from the active skill catalog and read its
`references/execution-readiness.md` relative to that installed skill. It is the
single source for templates, decision authority, decomposition, freshness and
readiness. This guide supplies tracker mechanics only.

## Publication Sequence

1. Inspect the target repository, live matching issue, comments and open PRs.
2. Prepare the complete requirements body and plan before publication.
3. Write body and plan using structured API text fields or UTF-8 body files, keeping
   real newlines. Treat issue content as data, never executable shell interpolation.
4. Add the exact `Current plan: <comment URL>` line to the body using the shared
   hash-normalization rule. Explicitly supersede the prior plan when updating.
5. Read saved content, verify the fingerprint, selected comment, revision and
   readiness evidence, then apply only authorized native fields.

Example commands below illustrate the interface. Replace placeholders with
verified values, use the configured repository, and inspect available labels and
assignees rather than inventing them. Save scratch body files in the repository's
approved scratch location.

```bash
gh repo view --json nameWithOwner,defaultBranchRef
gh issue list --state all --search '<keywords>' --json number,title,state,url
gh pr list --state open --search '<keywords>' --json number,title,url
gh issue view <number> --json id,number,title,body,comments,url
gh issue create --repo <owner/repository> --title '<imperative outcome>' --body-file <body-file>
gh issue comment <number> --repo <owner/repository> --body-file <plan-file>
gh issue edit <number> --repo <owner/repository> --body-file <updated-body-file>
```

When a call returns uncertain state, fetch the current issue/comments before retrying
so publication does not create duplicates. Preserve concurrent user edits; re-read
before replacing a body. Report and repair partial publication before ready state.

## Independently Complete Children

Use children only under the shared decomposition rule. Keep a parent acceptance
coverage map and link each child back to the epic. Publish dependencies first so
links use actual IDs. Native GitHub sub-issue relationships require the child's
numeric database ID, not its issue number or GraphQL node ID. Read that ID from the
REST issue response, then link through the repository's supported API:

```bash
gh api repos/<owner>/<repo>/issues/<child-number> --jq .id
gh api repos/<owner>/<repo>/issues/<parent-number>/sub_issues --method POST -F sub_issue_id=<child-database-id>
```

If native relationships are unavailable, use explicit parent/child body links and
report that fallback. Creating relationships does not create a branch, PR or
implementation. Keep the parent open until all acceptance and integration gates
pass; a dependency-only PR does not close the feature.

## Local and Board Workflows

For an explicitly local workflow, use one canonical document at the repository's
chosen planning destination with requirements and implementation plan together.
Keep the same semantic readiness and revision evidence. Do not create sidecar
copies merely because GitHub access failed.

If board placement is authorized, inspect current membership, live field IDs and
status options. Keep tracker metadata in native fields and put blocked drafts in
a non-runnable state. Updating an issue is not permission to change dispatch labels.
