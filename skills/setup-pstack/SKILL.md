---
name: setup-pstack
description: "Configures canonical Shipshit Pstack adapters for selected harnesses while preserving existing role choices. Use when setting up Pstack, migrating duplicate installations, or enabling a supported optional adapter."
disable-model-invocation: true
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.2"
  tags: "pstack, workflow"
  source: https://github.com/ericlitman/open-pstack
  upstream_commit: 1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43
  last_synced: "2026-09-05"
---

# Setup Pstack

Configure the installed Shipshit distribution without enabling another Pstack
plugin. This is an explicit setup workflow, not a session-start side effect.

## Contract

Inputs:

- Target harnesses and the user's current canonical role configuration.
- Installed Shipshit skill paths and authorized setup actions.

Outputs:

- A reviewed adapter plan, backups, installed adapter paths and probe evidence.

Creates/Modifies:

- Only approved harness adapters and their bounded configuration registrations.

External Side Effects:

- Selected model probes may incur usage. Optional automation setup creates only
  the explicitly selected routine after its project, schedule and actions are set.

Confirmation Required:

- Configuration writes or paid probes not already covered by the request.

Delegates To:

- File pointer: provider dispatch and setup resources in the installed pstack skill.

## Workflow

1. Resolve the installed `pstack` skill through the active catalog. Read its
   `references/provider-dispatch.md` and `adapters/README.md`.
2. Inventory existing model sheets, generated adapters, startup hooks, skill links
   and plugins. Identify the source of truth before editing generated files.
   Preserve role assignments, accounts and host restrictions.
3. Render a concrete plan with old and new paths, exact registration changes and
   rollback. Resolve installed paths absolutely; do not assume a plugin root
   variable or a checkout of either upstream repository.
4. Bind only user-selected roles. Validate explicit provider/model/effort values
   against that provider's current supported interface. Never require an unused
   provider just to fill an upstream four-model matrix.
5. Probe authorized selected lanes on the approved execution host. Use native
   delegation for same-provider lanes and the bundled runner for external lanes.
   Record route, model, requested effort, output and receipts. Failed probes leave
   current configuration untouched; report unavailable routes.
6. Back up every target. Apply the reviewed source changes, regenerate adapters
   when the harness uses a generator, and compare read-back bytes. Restore all
   affected targets if any write or validation fails. An unchanged rerun must
   produce identical configuration.
7. Verify a fresh session discovers canonical Shipshit entries and exercises one
   representative workflow. Disable duplicate plugin registrations only after
   this replacement works. Remove only links proven to point to the replaced
   distribution. Keep unrelated skills and rollback backups.
8. For Benny or Bot UI, first check the explicit capability gates in
   `pstack/adapters/README.md`. Report unsupported platform capabilities.
   Installation of this skill alone does not schedule routines or expose a server.

Report configuration paths, preserved role choices, probe evidence, active
entrypoints and rollback instructions. Distinguish static validation from live
behavioral verification.
