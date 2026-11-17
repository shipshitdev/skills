# Verify Check

One report-only verification pass. Run a target's checks against the real thing and
return findings that someone else can reproduce without asking questions. Changes no
source, no data the check did not create, and no configuration.

## Contract

Inputs:

- A target: a QA report path, an issue or PR number, a command, or a URL with cases
- Optional `--surface local|preview|prod` (default `local`)

Outputs:

- A verification set (what was checked) and a findings list, written to
  `.tmp/verify/<run-id>/findings.md` and returned to the caller
- A verdict: green when every check passed, otherwise red with the finding count

Creates/Modifies:

- Scratch under the repository's `.tmp/` only; runner artifacts at their default locations
- Starts the app locally when the checks need it, and stops what it started

External Side Effects:

- Runs the repository's check commands; for app-driven checks, requests against the
  surface's origin only. On `prod`, follow the safety rules in `qa/references/prod.md`
  (QA account only, credentials from the environment, no unsafe actions).

Confirmation Required:

- None for read-only checks. Ask before any step the surface's safety rules mark unsafe.

Delegates To:

- Run a delegate by reading its playbook under the installed skills directory and following it
  (`/<router> <action>`: `<router>/references/<action>.md`; `/<name>`: `<name>/SKILL.md`);
  skills here are user-invoked only, so the Skill tool cannot load them.
- `/qa prod` (`qa/references/prod.md`) when the target is a release to verify on production
- `/test` (`test/SKILL.md`) for the repository's own test scopes

## Build the verification set

Turn the target into a flat list of checks, each with an id, a kind, a command or steps,
and the expected result. Kinds:

- **automated**: a command the repository documents (tests, type-check, lint, build).
  Prefer the narrowest scope that covers the change, then the repository's full gate once.
- **app-driven**: steps against the running app: a browser path or an HTTP call, with the
  route, the data used, and the observable expected result.
- **spec**: an acceptance criterion from an issue or PR, written in EARS form
  (`WHEN ... THE SYSTEM SHALL ...`). Each becomes one or more app-driven or automated
  checks. A criterion that cannot be observed is reported as `unverifiable`, never as pass.

From a QA report, each `fail` and `blocked` item is one check, using the report's repro
steps verbatim. From an issue or PR, read the body, the linked issue's criteria, and the
diff to find the adjacent flows it touches, and add a check per flow.

## Run

1. Order checks cheapest first (types, unit) then app-driven. Stop early only when a
   failure makes later checks meaningless (the app will not boot); mark those `blocked`.
2. Prove the real behavior: drive the user path rather than internal setters or test-only
   endpoints, capture the action and the resulting state, and verify side effects (record
   written, file produced, status changed) alongside what is visible. A page that merely
   renders is not a pass.
3. For app-driven checks, watch the browser console and failed same-origin requests
   after each interaction. An uncaught exception or 5xx during an otherwise passing path
   is its own finding.
4. A mock counts only where a production boundary already isolates the external system.
   When using a dry-run or test mode, observe what it actually skips rather than trusting
   its name.
5. Re-run each failing check once from a clean state. A failure that disappears is
   `flaky` (record both outcomes and the conditions); it is never silently green.
6. Never alter a check to get a result. If the expectation looks wrong, report the
   failure and note the doubt.

## Finding format

One entry per distinct failure. Deduplicate by signature.

```markdown
### F<n>: <one-line symptom>
- Check: <id, kind>
- Surface: <local|preview|prod>, build <sha or version>
- Repro: <one command, or numbered steps; deterministic, from a clean state>
- Expected: <result>
- Actual: <result, with the key output verbatim>
- Signature: <normalized: first error line or failing assertion, route and status>
- Evidence: <paths to screenshots, traces, logs; redacted>
- Flaky: no | yes (<n> of <m> runs failed)
```

A finding with no repro command or steps is not a finding; it is a note under "Unconfirmed".

## Output

```text
Verdict: GREEN | RED (<n> findings)
Surface: <...>  Build: <...>
Checked: <n> automated, <n> app-driven, <n> spec   (<n> unverifiable, <n> blocked)
Findings: F1 <symptom>; F2 <symptom>
Unconfirmed: <notes that lack a repro>
Findings file: <path>
```

State what was not run and why. Green means every check in the set passed, nothing more.
