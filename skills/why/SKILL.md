---
name: why
description: "Investigates why code is shaped as it is: design rationale, regressions, postmortems, data-backed thresholds, with cited evidence. Use how for runtime behavior."
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.2"
  tags: "investigation, rationale, history, evidence"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/why/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "why was this built this way, decision history"
---

# Why

Investigate the motivation behind code. Companion to `how`. `how` answers
what the code does. `why` answers what forces led to its shape.

Historical context spreads across seven evidence categories. Enumerate
available connectors at run time, query every available category in
parallel, then synthesize with explicit confidence calibration. A null
result is first-class evidence.

## Contract

Inputs:

- A why-question about a chunk of code, pattern, feature, or named decision

Outputs:

- A confidence-separated, cited narrative with a coverage map

Creates/Modifies:

- None

External Side Effects:

- Read-only git, `gh`, and available issue/docs/chat/observability
  connectors. No writes.

Confirmation Required:

- None

Delegates To:

- None. May spawn one investigator per evidence category, then one
  synthesizer.

## Operating posture

- Evidence before narrative.
- Precision over polish. Quote and cite.
- Name the gaps.
- Hedge when evidence is indirect.
- Do not infer intent from code shape alone.

Read [references/epistemics.md](references/epistemics.md) before
synthesizing.

## Step 1. Understand the target

Parse the question. If the target is vague, state the best guess from
conversation context and proceed.

## Step 2. Establish the code anchor

Before spawning investigators, gather file paths, line ranges, key
symbols, recent commits, and PR numbers.

```bash
git blame -L <start>,<end> <file>
git log --follow -p -- <file>
git log --oneline -20 -- <file>
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

Pass this seed to every investigator.

## Step 3. Spawn parallel investigators

Discover available connectors (MCP servers, CLIs, APIs). Map each to one
category from [references/evidence-categories.md](references/evidence-categories.md).
Source control is always available through git and `gh`.

Launch one investigator per available category in a single message, on
the fast cheap tier. Do not use a read-only sandbox that strips
connectors. Investigators still write nothing.

Skip a category only with a written justification: no connector
available, or the source is provably irrelevant. "Probably irrelevant"
is not enough.

Each investigator gets [references/investigator-prompt.md](references/investigator-prompt.md),
its category playbook, the code anchor, and the user's question.

## Step 4. Synthesize

Spawn one synthesizer on the strongest judgment tier. It gets all
findings, including nulls, plus
[references/synthesizer-prompt.md](references/synthesizer-prompt.md)
and the epistemics file. Do not rewrite its confidence language.

## Output format

**The Question.** Restate the ask.

**The Code in Question.** Paths, line ranges, symbols.

**What We Found (direct evidence).** Cited claims only.

**What We Can Reasonably Infer.** Hedged, with the inference chain.

**Competing Hypotheses.** When the record supports more than one story.

**What We Don't Know.** Specific gaps.

**Sources Consulted.** One line per category, including empties and
skips.

If the why is a precursor to a change, convert findings into Preserve /
Change / Avoid / Risk constraints.

## Why procedure

Read [why procedure](references/why-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
