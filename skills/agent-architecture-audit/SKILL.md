---
name: agent-architecture-audit
description: Audits LLM agent apps for wrapper regressions, prompt or memory contamination, tool misuse, and hidden retry loops. Use when an agent fails in-product but works as a direct call.
metadata:
  version: "2.2.3"
  tags: "agents, llm, architecture, audit, debugging"
when_to_use: "before shipping agent features"
---

# Agent Architecture Audit

Diagnose failures in agent systems by inspecting each layer between the raw model call and the user-visible output.

## Contract

Inputs:

- Agent or LLM application repository, failing run, trace, log, or symptom
- Optional model/provider list, tool definitions, memory files, and UI output

Outputs:

- Severity-ranked findings with evidence references
- Layer-by-layer failure diagnosis
- Ordered fix plan that prefers code gates over prompt-only changes

Creates/Modifies:

- None in audit mode
- Follow-up fixes only when explicitly requested

External Side Effects:

- None by default
- External logs, observability tools, or production systems only when already authorized

Confirmation Required:

- Before changing prompts, memory, tool contracts, persistence, production config, or user data

Delegates To:

- `debug` for ordinary software defects
- `evaluation` (including its LLM-as-judge mode) for benchmark design
- `security-audit` for prompt injection, secrets, auth, or privileged tool risk

## When to Use

- An agent works in a model playground or direct API call but fails in the app.
- A wrapper, orchestration layer, memory system, or tool router was added and
  quality regressed.
- The model skips required tools, claims tool use that did not happen, or
  misreads tool output.
- Old conversation facts, stale memories, or compressed summaries leak into new
  tasks.
- Logs show a correct answer but the CLI, API, UI, streaming layer, or renderer
  shows a different result.
- Hidden retry, fallback, repair, or summarization loops may be mutating output.

Do not use for general code review — only when the failure is likely in the agent stack.

## Layer Model

Audit the stack from source instructions to delivered output:

| Layer | What Can Fail |
| --- | --- |
| System prompt | Conflicts, bloat, stale rules, unclear priorities |
| Session history | Old turns dominate or contradict the current task |
| Long-term memory | Cross-project leakage, stale preferences, agent-written facts |
| Distillation | Compaction turns guesses into pseudo-facts |
| Active recall | Redundant summaries waste context or revive old context |
| Tool selection | Required tools are optional in code, not enforced |
| Tool execution | Missing calls, failed calls, unvalidated arguments |
| Tool interpretation | Output is ignored, overtrusted, or read backward |
| Answer shaping | Format, schema, markdown, or JSON is changed after reasoning |
| Transport/rendering | Streaming, API, CLI, or UI mutates valid content |
| Hidden repair loops | A second model pass silently rewrites the answer |
| Persistence | Cached artifacts or expired state are reused as live evidence |

## Audit Process

### 1. Scope the System

Identify:

- user entrypoints and output surfaces
- model providers, model tiers, and retry/fallback behavior
- prompt assembly path and instruction sources
- memory, retrieval, compaction, and persistence paths
- tool schemas, tool routing, and execution validation
- known symptoms and the first release or commit where they appeared

### 2. Collect Evidence

Search for:

- prompt templates and instruction injection points
- tool schemas, routers, validators, and execution logs
- memory admission, retrieval, and compaction code
- provider calls outside the primary agent loop
- fallback, retry, repair, or output rewriting passes
- response serialization, markdown rendering, JSON parsing, and stream handling

Prefer file and line evidence. Compare raw model output, post-processed output, transported output, and rendered output when logs are available.

### 3. Map Failure Mechanisms

For each suspected issue, record:

- symptom: what the user sees
- layer: where the corruption enters
- mechanism: how the layer changes behavior
- root cause: code, config, prompt, memory, transport, or process
- evidence: file, line, trace id, log row, or reproduced run
- confidence: high, medium, or low

### 4. Prioritize Fixes

Prefer fixes in this order:

1. Enforce required tool use in code.
2. Remove or expose hidden repair and fallback agents.
3. Reduce duplicated context across prompt, memory, history, and summaries.
4. Tighten memory admission so user corrections outrank agent assertions.
5. Narrow compaction triggers and preserve uncertainty markers.
6. Pass through already-valid output instead of rewriting it.
7. Use typed envelopes for internal protocol boundaries.
8. Add trace tests that compare raw, processed, transported, and rendered output.

Do not solve tool discipline, memory safety, or transport corruption only by adding stronger prompt wording.

## Severity

| Severity | Meaning |
| --- | --- |
| Critical | The system can confidently perform wrong or unsafe operational behavior |
| High | Correctness or stability degrades frequently under normal use |
| Medium | The agent usually works, but the stack is fragile, wasteful, or hard to debug |
| Low | Maintainability, observability, or cosmetic output issues |

## Output Format

Lead with findings:

```markdown
## Findings

| Severity | Layer | Finding | Evidence | Fix |
| --- | --- | --- | --- | --- |
| High | Tool selection | Required retrieval is prompt-only and can be skipped | `src/agent/router.ts:42` | Gate final answer on retrieval result |

## Diagnosis

[Explain which layer corrupts the behavior and why.]

## Fix Plan

1. [Code-first fix]
2. [Validation]
3. [Follow-up hardening]
```

If no issues are found, say so and list the evidence checked plus remaining
blind spots.

## Anti-Patterns

- Blaming the model before testing wrapper-layer behavior.
- Accepting "must use tool" prompt text when no code enforces the requirement.
- Treating compressed summaries as ground truth.
- Allowing hidden model passes to rewrite final output without traceability.
- Reporting green status without comparing internal output to delivered output.
