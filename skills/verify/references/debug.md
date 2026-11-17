# Verify Debug

Find the root cause of one failing finding. The skill is the feedback loop: a fast,
deterministic command that fails the way the finding fails. Every claim after that is
tested against it. Changes no source; temporary instrumentation is removed before the
playbook ends.

## Contract

Inputs:

- One finding: repro, expected, actual, signature, evidence (from `check`, a QA report,
  or the user)
- The surface it failed on, and the loop branch when run from `loop`

Outputs:

- The red-capable repro command (the tightest one found)
- The root cause: the first place the system went wrong, with the evidence that proves
  it, and a confidence of `proven` or `likely`
- A fix direction in one or two sentences, and what a regression check should assert
- A record of refuted hypotheses, so no later attempt repeats them

Creates/Modifies:

- Scratch repro scripts under the repository's `.tmp/`
- Temporary instrumentation in source, tagged `[VERIFY-DEBUG-<id>]` and removed before returning.
  Confirm with a search for the tag that none remain.

External Side Effects:

- Runs the repro and the app locally. On `prod`, only read-only observation as the QA account
  within the rules in `qa/references/prod.md`; never reproduce by changing production data
  the run did not create.

Confirmation Required:

- None for read-only diagnosis. Ask before touching shared data, enabling production debug
  flags, or running anything the surface's safety rules mark unsafe.

Delegates To:

- Run a delegate by reading its playbook under the installed skills directory and following it
  (`/<router> <action>`: `<router>/references/<action>.md`; `/<name>`: `<name>/SKILL.md`);
  skills here are user-invoked only, so the Skill tool cannot load them.
- Upstream mattpocock `diagnosing-bugs`, when installed, for a stubborn bug after this
  playbook's attempt budget is spent. Run its installed playbook instead of improvising.

## Phase 1: Build the feedback loop

Do this before forming any theory. If you catch yourself reading code to build a
hypothesis and no command reproduces the failure yet, stop and build the command.

Pick the cheapest loop that fails the same way the finding does, in order:

1. The finding's own repro command or steps, if they already fail deterministically.
2. A failing automated test at the nearest seam (unit, integration, or route handler).
3. A scripted HTTP call (`curl` or a small script) against the local app with the same
   inputs.
4. A headless browser script that drives the same path and asserts the same observable.
5. A replay of captured input: a recorded request, a fixture, a log line, a saved HAR.
6. A bisect over history (`git bisect run <command>`) when it worked before.
7. A differential: the same input against the last good build or a known good account.

Make it fast and sharp: seconds, not minutes; one assertion that fails for the right
reason and for nothing else. It must run from a clean state and fail the same way three
runs in a row. If it is flaky, raise the rate first by looping it or pinning time, seed,
or ordering, then debug a failure that fires on demand.

When the symptom exists only on production, reproduce it locally with the QA fixtures or an
equivalent seed. If that is not possible after a bounded effort, report
`not reproducible off prod` with what was tried; do not guess.

## Phase 2: Minimize

Shrink the repro until removing anything more makes it pass: the smallest input, the
fewest steps, the least data. The minimal repro usually names the cause.

## Phase 3: Hypothesize

Write three to five ranked, falsifiable hypotheses. Each states a cause and the
observation that would refute it ("if X is the cause, then Y logs Z; if not, W"). Rank by
likelihood and by cost of testing. Test the cheapest discriminating observation first.
Read `git log` and blame for the failing area: a regression has a suspect commit.

## Phase 4: Instrument and discriminate

Add the least instrumentation that separates the hypotheses (a log at a boundary, an
assertion, a breakpoint-equivalent print), tagged `[VERIFY-DEBUG-<id>]`. Run the repro, read
the output, and eliminate. Update the hypothesis list after each run: refuted, supported, or
unclear. Stop at the first hypothesis that survives a test designed to refute it. Prefer
evidence from the running system over reading code.

If two hypotheses survive, find the observation that splits them. If none survive, the
premise is wrong: write down what you assumed, test it directly, and restart Phase 3.

## Phase 5: State the cause

The root cause is the earliest point where behavior diverges from what the code's own
contract or the spec requires, not the place the symptom surfaced. A guard that hides a
bad state is not a cause. Check that the cause explains every symptom in the finding and
nothing contradicts it. Then:

- Remove all instrumentation; search for the tag to confirm.
- Return the result in this shape.

```text
Finding: <id> <symptom>
Repro: <command>                      (fails in <s> seconds, <n>/<n> runs)
Root cause: <file:line or component, and why it is wrong>
Evidence: <the observation that proves it, trimmed, verbatim>
Confidence: proven | likely            (likely needs one more discriminating run before an edit)
Fix direction: <smallest change that removes the cause>
Regression check should assert: <observable behavior>
Refuted: <hypothesis> because <observation>; ...
Instrumentation removed: yes
```

## Budget

Spend at most three discriminating cycles per attempt without a surviving hypothesis. Then
widen the loop, question the premise, or report `stalled` with the refuted list so the
caller can stop or escalate. Never fix by guessing.
