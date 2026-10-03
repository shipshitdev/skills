<!-- Upstream: obra/superpowers skills/systematic-debugging/SKILL.md @ 030a222af19c
(MIT, last synced 2026-06-12). Folded into `debug` on 2026-10-03 (#168); the four
phases, the Iron Law, and the red flags are unchanged from upstream. -->

# Systematic Debugging

## Core Principle

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

If Phase 1 is not complete, no fix may be proposed.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

## Entry Point

The `debug` front door hands cases here on escalation, carrying its loop, its
evidence, and its attempt count. Start at Phase 1 regardless and re-verify that
evidence; an escalated case is escalated because the earlier read was wrong
somewhere.

## When to Use

Enter this loop once a first pass has already been spent on any technical issue —
a test failure, a production bug, a performance problem, a build break, an
integration fault:

- A fix attempt failed
- The same defect returned after a previous fix
- Each fix exposes a new problem somewhere else
- The failure spans components and the boundary evidence is missing
- The cause must be proven before another line changes

Enter directly, skipping the front door, when:

- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- A fix already feels obvious while the issue is not fully understood

Complete the whole process even when:

- The issue seems simple (simple bugs have root causes too)
- You are in a hurry (rushing guarantees rework)
- Stakeholders want it fixed immediately (systematic is faster than thrashing)

## The Four Phases

Complete each phase before proceeding to the next.

---

### Phase 1: Root Cause Investigation

**Before attempting ANY fix:**

**1. Read error messages carefully.**

- Do not skip past errors or warnings — they often contain the exact solution.
- Read stack traces completely.
- Note line numbers, file paths, error codes.

**2. Reproduce consistently.**

- Can you trigger the failure reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible: gather more data. Do not guess.

**3. Check recent changes.**

- What changed that could cause this?
- Review git diff, recent commits, new dependencies, config changes, environment differences.

**4. Gather evidence in multi-component systems.**

When a system has multiple components (e.g., API → service → database, CI → build → signing):

Before proposing any fix, add diagnostic instrumentation at each component boundary:

```
For EACH component boundary:
  - Log what data enters the component
  - Log what data exits the component
  - Verify environment / config propagation
  - Check state at each layer

Run once to gather evidence showing WHERE it breaks.
Analyze evidence to identify the failing component.
Then investigate that specific component.
```

Example instrumentation pattern:

```bash
# Layer 1: entry point
echo "=== Input at layer 1: ${VAR:+SET}${VAR:-UNSET} ==="

# Layer 2: downstream component
echo "=== Env vars reaching layer 2: ==="
env | grep VAR || echo "VAR not in environment"

# Layer 3: leaf operation
echo "=== State at layer 3: ==="
# inspect relevant runtime state here
```

This reveals which layer fails (e.g., value passes layer 1 but is missing at layer 2).

**5. Trace data flow.**

When an error is deep in a call stack:

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing up until you find the source.
- Fix at the source, not at the symptom.

---

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find working examples.** Locate similar working code in the same codebase.
2. **Compare against references.** If implementing a pattern, read the reference implementation completely — do not skim.
3. **Identify differences.** List every difference between working and broken, however small. Do not assume "that can't matter."
4. **Understand dependencies.** What config, environment, or assumptions does the component require?

---

### Phase 3: Hypothesis and Testing

**Apply scientific method:**

1. **Form a single hypothesis.** State clearly: "I think X is the root cause because Y." Be specific.
2. **Test minimally.** Make the smallest possible change to test the hypothesis. One variable at a time.
3. **Verify before continuing.**
   - Did it work? Yes → proceed to Phase 4.
   - Did not work? Form a NEW hypothesis. Do not add more fixes on top of the failed one.
4. **When you do not know:** say so. Ask for help or gather more evidence. Do not pretend to understand.

---

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create a failing test case** — the simplest possible reproduction — automated if a test framework exists, a one-off script otherwise. This must exist before the fix is written.

2. **Implement a single fix.** Address the identified root cause. One change at a time. No "while I'm here" improvements or bundled refactoring.

3. **Verify the fix.**
   - Does the test now pass?
   - Are other tests still passing?
   - Is the issue actually resolved?

4. **If the fix does not work:**
   - STOP.
   - Count: how many fixes have been attempted?
   - If fewer than 3: return to Phase 1 and re-analyze with the new information.
   - If 3 or more: see step 5.

5. **If 3+ fixes have failed — question the architecture.**

   Signs of an architectural problem:
   - Each fix exposes new shared state, coupling, or a problem in a different place.
   - Fixes require massive refactoring to implement.
   - Each fix creates new symptoms elsewhere.

   Stop and question fundamentals:
   - Is this pattern fundamentally sound?
   - Are we continuing out of inertia rather than evidence?
   - Should the architecture be redesigned rather than another patch applied?

   Discuss with the user before attempting any further fixes. This is not a failed hypothesis — it is a wrong architecture.

---

## Red Flags — Stop and Return to Phase 1

If any of these thoughts arise, stop immediately:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when 2+ have already failed)
- Each fix reveals a new problem in a different place

**All of these mean: STOP. Return to Phase 1.**

If 3+ fixes have failed: question the architecture (Phase 4, step 5).

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is faster than guess-and-check thrashing. |
| "Just try this first, then investigate" | The first fix sets the pattern. Do it right from the start. |
| "I'll write the test after confirming the fix works" | Untested fixes do not stick. A test first proves it. |
| "Multiple fixes at once saves time" | Cannot isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms does not equal understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, do not fix again. |

---

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|----------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare against broken | Differences identified |
| **3. Hypothesis** | Form specific theory, test minimally | Confirmed or new hypothesis formed |
| **4. Implementation** | Create failing test, apply single fix, verify | Bug resolved, tests pass |

---

## When Investigation Reveals No Root Cause

If systematic investigation genuinely reveals the issue is environmental, timing-dependent, or fully external:

1. You have completed the process correctly.
2. Document what was investigated and what was ruled out.
3. Implement appropriate handling (retry logic, timeout, error message).
4. Add monitoring or logging for future investigation.

Note: 95% of "no root cause found" cases are incomplete investigation. Exhaust Phase 1 fully before concluding this.

---

## Impact

- Systematic approach: 15–30 minutes to resolution.
- Random-fix approach: 2–3 hours of thrashing.
- First-time fix rate: ~95% vs ~40%.
- New bugs introduced: near zero vs common.
