# PRD Task Creator

Publish the shared preparation packet. This engine owns tracker mechanics and
relationships; requirements, implementation planning and readiness stay with their
respective engines.

## Contract

Inputs:

- Prepared packet or rough request, target issue/repository, and authorized actions.
- Optional parent epic, labels, assignee, priority, or canonical local destination.

Outputs:

- Verified issue/body and current plan links, readiness result, and relationships.
- Draft content with blockers when publication or execution readiness is unavailable.

Creates/Modifies:

- Requested issues, plan comments, current-plan links, and authorized sub-issue links.
- One local canonical document only for an explicitly local workflow.

External Side Effects:

- Tracker reads and authorized issue/comment writes. No implicit branch creation,
  implementation, board dispatch, merge, or deployment.

Confirmation Required:

- Existing authorization to create/update these work items covers publication.
  Ask only for missing or expanded authority. Draft/report-only callers stay draft.
  Prepare the full packet before any required publication approval.

Delegates To:

- Run a delegate by reading its playbook under the installed skills directory and following it
  (`/<router> <action>`: `<router>/references/<action>.md`; `/<name>`: `<name>/SKILL.md`);
  skills here are user-invoked only, so the Skill tool cannot load them.
- `/issue feature` for a rough request without a prepared packet.
- `/issue check` for canonical templates and readiness validation.

## Publish the packet

1. Resolve the target from the user/session and verified repository remote. Search
   existing issues and open PRs. Reuse the matching issue within authorized scope;
   never overwrite unrelated work. Missing GitHub access is a publication blocker,
   not authority to create unrequested local memory files.
2. If the input is a rough request, run `/issue feature` and return its
   result. Its call back into this engine carries a prepared packet, preventing
   recursive preparation. For an explicit requirements-only/draft issue, publish
   the draft within scope but keep it non-runnable.
3. Load the shared readiness/decomposition reference through `/issue check`.
   Default to one complete feature issue and one PR. Split only independently
   complete outcomes, never backend/frontend/E2E ticket templates. Publish necessary
   dependencies first, link real IDs, and preserve parent acceptance coverage.
4. Run `/issue check` in `execution-readiness` mode for an execution
   packet. Keep blocked packets off the runnable path even if their drafts may be
   published. Do not label unresolved planner decisions AFK.
5. Preserve live tracker metadata and current user edits. Write requirements as the
   issue body and the complete plan as a `## Implementation Plan` comment. Bind it
   using the shared revision, SHA, fingerprint, and verdict protocol; set the
   current-plan link and identify superseded plans.
6. Fetch the saved body and current comment again. Verify their identity, content,
   fingerprint and links; re-run readiness against the saved packet and current
   source. If a write partially fails, report the partial state and repair within
   authorized scope before changing readiness/dispatch state. A local READY draft
   does not prove the published issue is ready.
7. Set only requested/authorized native fields using inspected live IDs/options.
   Record AFK only for a verified READY packet. Keep human-only blockers distinct
   from planner-owned rework. Return URLs and the readiness verdict, including any
   remaining publication or delivery blockers.

## Tracker mechanics

Use the procedures in [Publishing guide](publish-guide.md). They contain
tracker details only. Resolve templates through `/issue check`, never maintain
an alternate agent brief or weaker readiness checklist here.
