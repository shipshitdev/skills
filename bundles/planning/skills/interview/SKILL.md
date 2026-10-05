---
name: interview
description: Repo-grounded discovery interview that produces a handoff brief for PRD writing, feature intake, or planning.
user-invocable: true
disable-model-invocation: true
argument-hint: "[topic, feature, issue, or decision]"
metadata:
  version: "2.2.2"
  tags: "interview, discovery, requirements, planning"
  author: Ship Shit Dev
when_to_use: "interview me, grill me, grill me with docs, discovery interview, requirements interview, before PRD, clarify requirements, /interview"
---

# Interview

Run a focused discovery interview before creating a PRD, writing a plan, shaping
UX, or starting implementation. Ground in the repo first, then run `grilling` for
the decisions that cannot be inferred.

This skill does not write code, create issues, or produce a final PRD by default.
It produces an interview brief. Recommend the next skill; do not invoke another
user-invoked skill.

## Contract

Inputs:

- Rough feature idea, issue number, product decision, bug class, or architecture
  question.
- Optional docs, links, transcripts, screenshots, or existing tracker context.

Outputs:

- Concise context scan summary.
- Settled decisions from `grilling`.
- Final interview brief ready for `prd-writer`, `feature-intake`, `shape`,
  `/prd spec`, or direct implementation.

Creates/Modifies:

- None by default.
- May write tracker comments, PRD bodies, or memory files only when explicitly
  requested after the interview.

External Side Effects:

- None by default.
- Reads local repo context and, when needed, tracker or linked documentation.
- Writes external systems only after explicit approval.

Confirmation Required:

- Before creating or editing GitHub issues, PRDs, comments, memory files, or
  other durable artifacts.

Delegates To:

- `grilling` for the design-tree interview (frontier rounds, recommended answers).
- `domain-modeling` when a term crystallizes or conflicts with `CONTEXT.md`.

Recommend next (do not invoke): `prd-writer`, `feature-intake`, `shape`,
`/prd spec`, `prd-quality-gate`.

## When To Use

- A user asks for `/interview`, "grill me", "grill me with docs", or equivalent.
- A feature idea is too vague to turn directly into a PRD.
- Existing repo docs probably answer part of the question, but missing decisions
  still need the user.

Skip this skill when:

- The user already provided a complete PRD or issue with acceptance criteria.
- The request is a small, obvious edit and the user said to implement directly.
- The only missing context is discoverable from the repo with no user decision.

## Workflow

### 1. Ground In Repo Context

Read repo context before asking questions:

- Start with `.agents/README.md` when present.
- Read relevant `.agents/memory/` files, especially `.agents/memory/memory.md`,
  `.agents/memory/context.md`, and any task-relevant `.agents/memory/system/`
  docs.
- Read `CONTEXT.md` / `CONTEXT-MAP.md` and `docs/agents/domain.md` when present.
- Check recent `.agents/sessions/` entries only when they are relevant to the
  topic.
- Read the applicable `AGENTS.override.md` / `AGENTS.md` chain for routing and
  repo rules. Read `CLAUDE.md` when the active workflow is Claude-specific.
- Search docs, README files, source code, and issues for the topic before
  asking the user to repeat known context.

Do not look for a local plans directory under `.agents`; plans live on GitHub
issues and PR comments.

When the user provides external docs or says "with docs", read only the relevant
sections and keep a short source list for the final brief.

### 2. State What Is Known

Before asking questions, summarize the context scan in three compact bullets:

- What the repo already says.
- What is still ambiguous.
- Which downstream artifact this interview is likely feeding.

If the repo gives enough context, ask for confirmation instead of running a long
interview.

### 3. Run grilling

Run the `grilling` skill on the remaining decisions. It owns the design tree,
the **frontier**, recommended answers, and the facts-vs-decisions split.

When a term is resolved or conflicts with `CONTEXT.md`, run `domain-modeling`
inline.

### 4. Stop At The Right Time

Stop when one of these is true:

- The grilling **frontier is empty** and the brief can feed the next skill.
- Remaining questions are implementation details for the planner or executor.
- The user says "enough", "write it", "make the PRD", or equivalent.
- A blocker requires a separate research pass, stakeholder decision, or external
  access.

## Final Interview Brief

End with this structure:

```markdown
## Interview Brief: <topic>

### Context Read
- <files, issues, docs, or links used>

### Problem And User
<who has the problem, where it appears, and why it matters>

### Desired Outcome
<what must be true after the work ships>

### Version-One Scope
- <included behavior or decision>

### Non-Goals
- <explicitly excluded behavior or decision>

### Constraints And Dependencies
- <technical, business, timing, data, security, or UX constraints>

### Acceptance Signals
- <reviewable or testable completion signal>

### Risks And Open Questions
- <unresolved item, or "None">

### Recommended Next Step
<prd-writer | feature-intake | shape | /prd spec | direct implementation>
```

Keep the brief concise enough to paste into a tracker issue or hand to a PRD
writer. Include inference notes when a fact came from repo context rather than
direct user confirmation.

Tell the user to run the recommended next skill. Do not fire it.

## Anti-Patterns

- Dump a long questionnaire before reading repo context.
- Turn the interview into a PRD unless the user asks.
- Ask questions whose answers are already in `.agents/memory/`, root
  agent files, docs, code, or tracker context.
- Save plans in local agent plan files.
- Start implementation during the interview.
- Invoke another user-invoked skill from this one.
