# Pstack upstream tracking

Shipshit maintains one canonical skill tree. Open Pstack supplies the portable
implementation; Cursor Pstack supplies the original implementation and capabilities
that the port does not include. Neither upstream plugin is a runtime dependency.

The accepted commits, complete file inventories, executable bits, and archive
checksums live in `lock.json`. The archives preserve source bytes and copyright
notices without exposing a second discoverable skill catalog. `mapping.json`
records each source file's canonical destination, adaptation reason, verification
reference, and accepted destination hash.

## Check the accepted import

Run from the repository on the verification host:

```bash
python3 scripts/pstack-sync.py verify
```

This command is offline and read-only. It rejects missing mappings, altered
archives, missing resources, unreviewed destination changes, and executable
procedures recorded only as archived metadata. Mapping coverage proves that files
are accounted for; runtime tests and installed-artifact reviews establish behavior.

## Review an upstream update

Use a clean checkout of the upstream repository. Fetch its current state and choose
a full commit SHA. Stage a candidate outside this repository, in the host's durable
artifact directory:

```bash
python3 scripts/pstack-sync.py candidate \
  --source open-pstack \
  --checkout /path/to/open-pstack \
  --commit FULL_40_CHARACTER_COMMIT_SHA \
  --output /path/to/artifacts/pstack-update
```

Repeat for `cursor-pstack` using the Cursor plugins checkout. Compare Open Pstack's
`UPSTREAM.md` marker before importing original changes already included in the port.

A lock source may declare `ignored_paths`, exact upstream paths or directory
prefixes ending in `/` that are repo-only and never shipped. Candidates skip and report them. Any other symlink or non-file
upstream object still fails staging, and an ignored path may not be archived or mapped.

The candidate includes an archive, proposed lock and mapping, an upstream diff,
and a report comparing accepted upstream, candidate upstream, and current local
adaptations. Added and changed files receive a pending disposition. Deleted files
leave the proposed mapping and remain visible in the removal report. The command
never changes canonical skills or advances the accepted lock.

Review every changed capability, including scripts, agent templates, hooks,
automation instructions, license notices, and packaging. Update the canonical
implementation and mapping on a feature branch. Copy the reviewed source archive
and corresponding source entry into the accepted lock; reconcile each mapping
explicitly. Preserve local authority boundaries and configured provider roles.
A new upstream model default is a review input, not a reason to replace user policy.

After reviewing intentional local adaptations, record their new hashes:

```bash
python3 scripts/pstack-sync.py record \
  --review-note "Reviewed canonical changes and their focused verification."
python3 scripts/pstack-sync.py verify
```

Recording hashes does not resolve pending mappings or attest behavioral parity.
Run the runtime regression suites, skill validation, packaging checks and independent
review before merging the accepted update. Keep the previous release available for
rollback.

## When to review

Review periodically and after a significant model or agent-harness release.
Compare real task outcomes before changing prompts or model routing. No scheduler
or automatic upstream promotion is enabled by this import.

## Installation cutover

Verify the complete Shipshit installation before disabling upstream providers.
Back up exact plugin registrations and owned links, preserve user-managed routing
sheets, and disable only duplicate Pstack providers. Keep inert source checkouts and
caches for rollback. A fresh agent session must resolve canonical skills and their
packaged resources before declaring the cutover complete.

Cursor-specific automation and bot UI adapters remain explicit setup workflows.
Their presence in the distribution does not create a routine, expose a webhook,
request credentials, or prove support on another harness.
