---
name: blast-radius
description: Finds what a small change could break elsewhere and proves it with real code. Use for blast radius of X, what could this break, or a small diff you do not trust.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.3"
  tags: "impact, safety, review, verification"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/blast-radius/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "is this small diff safe"
---

# Blast radius

Find what a change breaks somewhere else, before it ships. Companion
to `how` and `why`. Listing callers is not the job. The job is the
breakage grep will not show you.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A diff, PR, or proposed change that looks small

Outputs:

- What it does, the one safety fact (proven or marked unproven),
  confirmed risks, cleared checks, and the cheapest merge-time test

Creates/Modifies:

- An optional proof script under the current repo `.tmp/`

External Side Effects:

- Runs local proof scripts or tests. No production writes.

Confirmation Required:

- None for the analysis. Proof scripts stay local unless the caller
  commits them.

Delegates To:

- `why` step 2 for PR and commit anchors
- `arena` for a wide change that needs several independent reads

## How sure are you

For each safety fact, get as far down this list as is cheap, and say
where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line.
3. You walked the bad case and it does not reach.
4. You ran it. A script or test that calls the real code.
5. You reproduced it in the running app.

Any safety fact you cannot get to step 4, say so out loud.

## Steps

1. Read the change, including the part the diff does not spell out.
2. Find the one fact it is safe because of.
3. Look where grep stops: library source, pinned versions, timing,
   wire formats, feature flags, three hops downstream.
4. Be honest about each risk. Cite a real `file:line`. A search that
   finds nothing is still an answer.
5. Prove the one fact. Run real code. Paste what happened.
6. For a big or wide change, run it as an `arena`.

## What to hand back

- **What it does.** Including the part that is not obvious.
- **The one fact it is safe because of.** State it, say which step
  you got it to, and show the proof.
- **Risks.** Only the real ones.
- **Cleared.** What you checked and why it is fine.
- **Before you merge.** The cheapest test or repro that catches the
  real bug.

## Blast Radius procedure

Read [blast-radius procedure](references/blast-radius-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
