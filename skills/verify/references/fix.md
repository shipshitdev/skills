# Verify Fix

Fix one diagnosed finding: write the failing check first, make the smallest change that
turns it green, prove it, and commit. One finding, one commit.

## Contract

Inputs:

- One diagnosed finding with its repro, root cause, and confidence from `debug`
- The loop branch (or the current branch when run alone, after the branch check below)

Outputs:

- A regression check that failed before the fix and passes after, shown verbatim
- A conventional commit containing the fix and its check, and the result of the
  surrounding verification

Creates/Modifies:

- Source files needed for this root cause and the regression check's test file
- One local commit. Never touches CI, lint or test configuration, lockfiles, or `.env*`.

External Side Effects:

- Runs the repository's checks. No push, pull request, merge, or deploy.

Confirmation Required:

- Explicit invocation approves editing the files this finding's fix needs
- Stop and ask (or record `blocked` when unattended) before: changing a public API or
  data contract, a migration or data change, a dependency change, touching files outside
  the root cause's module and its direct callers, or a fix that needs materially different
  product behavior

Delegates To:

- Run a delegate by reading its playbook under the installed skills directory and following it
  (`/<router> <action>`: `<router>/references/<action>.md`; `/<name>`: `<name>/SKILL.md`);
  skills here are user-invoked only, so the Skill tool cannot load them.
- `/test` (`test/SKILL.md`) for focused test scopes when the repository's rules allow it
- Upstream mattpocock `tdd`, when installed, for a longer test-first session on a complex fix

## Rules

1. **Proven cause first.** Edit only when `debug` returned `proven`, or `likely` plus one
   discriminating run that supports it. Otherwise return to `debug`.
2. **Check first.** Before the fix, add the smallest check that encodes the expected
   behavior at the nearest seam, and run it to see it fail for the finding's reason. If a
   cheap automated check is impossible (a visual or third-party boundary), commit the repro
   script or steps as the check and say why. A check that passes before the fix proves
   nothing; fix the check.
3. **Smallest change.** Fix the root cause where it lives. No unrelated cleanup, renames,
   formatting sweeps, dependency changes, or new abstractions. Match the three nearest
   existing patterns for naming, structure, error handling, and test layout.
4. **Never lower the bar.** Do not loosen assertions, widen timeouts, add retries or sleeps,
   skip or delete tests, update a snapshot to match wrong output, or wrap the symptom in a
   try/catch. If the right change breaks another test, that test found a real conflict:
   resolve it on its merits or record `blocked`.
5. **Preserve data and baseline.** Never solve a local-state problem by deleting data,
   resetting the repository, or replacing environment files.

## Procedure

1. Confirm the current branch equals the loop branch (or, standalone, is not the default
   branch and has no unrelated uncommitted changes). Stop on mismatch.
2. Write the regression check; run it; capture the failing output.
3. Make the smallest fix for the stated root cause.
4. Run the regression check: it must pass. Run the finding's original repro and compare
   with the baseline: same route or command, same data, same viewport where it applies.
5. Run the narrowest broader scope that covers the touched module, then the repository's
   documented gate (types, lint, relevant tests) as its rules allow. A check the rules
   prohibit running here is recorded as not run, never as passed.
6. For a visual or interaction change, verify the affected state on the real surface
   rather than trusting compilation.
7. Review the diff: only the fix and its check, no debug tags, no secrets, no scratch
   files. Stage explicit paths. Commit with a conventional message that says what was
   wrong, for example `fix: keep exported CSV header order stable`. If a hook fails, fix
   the cause and retry; never bypass hooks.
8. Return:

```text
Fixed: <id> <symptom>
Cause: <root cause>
Check: <path or script>   before: FAIL (<key line>)   after: PASS
Verified: <repro result>; <scope> passed; <not run and why>
Commit: <short sha> <subject>
```

If three honest attempts leave the check red, revert uncommitted edits, return
`stalled` with what was tried and learned, and let the caller decide.
