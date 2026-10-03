---
name: execution-debugging
description: Scoped debugging methodology for when a test or build fails during execution/stabilization. Use to diagnose the failing check without scope-creeping — read the full error, reproduce in isolation, hypothesize before changing, localize, fix the root cause not the symptom, and guard with a regression test.
metadata:
  version: "2.2.2"
  tags: "debugging, testing, root-cause, stabilization, regression, execution"
user-invocable: false
---

<debugging_methodology>
<scope_constraint>
These steps apply ONLY to diagnosing the failing check.
Do not expand beyond the files touched in the original execution.
Do not redesign, refactor, or improve code outside the failure path.
</scope_constraint>

When a test or build fails during stabilization, follow this sequence:

1. READ the full error output — not just the last line. Stack traces, assertion messages, and build logs contain the diagnosis.

2. REPRODUCE the failure in isolation before changing anything.
   - Run the specific failing test or build step alone.
   - If it passes in isolation but fails in the suite, the problem is shared state or ordering.

3. HYPOTHESIZE explicitly before each change.
   - State what you believe is wrong and what evidence supports that belief.
   - Do not change code "to see if it helps."

4. LOCALIZE — narrow the failure to the smallest possible scope.
   - Is it in the code you wrote, or in existing code you called?
   - Is it a type error, a runtime error, or a logic error?
   - If it is in existing code, the plan may have an unstated assumption — surface it.

5. FIX the root cause, not the symptom.
   - Suppressing an error message is not a fix.
   - Adding a null check at the crash site when the upstream function should not return null is not a fix.
   - Changing the test expectation to match broken behavior is not a fix.

6. GUARD — write or update a test that fails without the fix and passes with it.
</debugging_methodology>
