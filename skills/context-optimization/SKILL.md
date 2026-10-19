---
name: context-optimization
description: "Improves context efficiency and diagnoses context degradation: budgets, masking, KV-cache, partitioning, lost-in-middle, poisoning. Use when token cost or context quality constrains a task."
metadata:
  version: "2.2.4"
  source: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-optimization/SKILL.md
  upstream_repo: muratcankoylan/Agent-Skills-for-Context-Engineering
  upstream_ref: main
  upstream_commit: 58b55a8921758d13453b440704fb1b5b208c0b0e
  last_synced: "2026-10-06"
  license: MIT
  tags: "context, optimization, degradation, agents"
when_to_use: "context window anatomy, attention, long-context failures, quality drops as context grows"
user-invocable: false
---

# Context Optimization Techniques

Context optimization extends the effective capacity of a limited context window through compression, masking, caching, and partitioning, applied with measurement discipline. The techniques below are ordered by impact and risk.

## When to use

- Context budgets or token costs constrain task complexity
- Verbose tool outputs could be replaced with retrievable references (observation masking)
- Prefix or KV-cache hit rate needs improvement
- Retrieval scoping could cut irrelevant loaded context
- Work could be partitioned across agents to extend effective capacity
- Budget triggers are needed for masking, compaction, or partitioning
- Agent quality drops as context grows, or output is wrong or irrelevant for no obvious reason (diagnose mode)

## Modes

| Mode | Use when | Read |
|------|----------|------|
| Optimize (default) | Token cost or budget limits the task and the context is behaving | This file, then [references/optimization_techniques.md](./references/optimization_techniques.md) |
| Diagnose | Quality has already dropped: lost-in-middle, poisoning, distraction, confusion, or clash | [references/degradation.md](./references/degradation.md), then [references/degradation-patterns.md](./references/degradation-patterns.md) for detection code and recovery |
| Explain | Onboarding to context mechanics with no active failure | [references/fundamentals.md](./references/fundamentals.md) |

Diagnose before optimizing a failing agent: compaction or masking applied to a poisoned or clashing context carries the error forward. First confirm the prompt works at low context length (if it fails at 2K tokens, the prompt is the problem), then match the symptom to a pattern and apply its first move:

| Pattern | Typical symptom | First move | Optimization tactic |
|---------|-----------------|------------|---------------------|
| Lost-in-middle | Correct fact in context is ignored; early instructions forgotten | Move critical content to the start or end; prepend a summary | Compaction that keeps key findings at the edges |
| Poisoning | A wrong claim persists after correction; tools misused | Truncate to before the bad claim and reload verified sources only | Restart with a clean partition |
| Distraction | Quality falls after loading extra documents | Filter retrieval before loading; put reference material behind tool calls | Retrieval scoping, observation masking |
| Confusion | Constraints or tools from another task leak in | Split tasks into separate contexts | Context partitioning |
| Clash | Contradictory sources give unpredictable answers | Set source precedence and drop outdated versions before loading | Retrieval scoping |

Trigger compaction well before the model-specific onset of degradation (about 70% of the known onset), not after symptoms appear.

## Core strategies

Apply in this priority order:

1. **KV-cache optimization.** Reorder and stabilize the prompt so the inference engine reuses cached Key/Value tensors. Cheapest option when the runtime supports prefix caching: low quality risk, immediate cost and latency savings. Apply first when stable prefixes exist.
2. **Observation masking.** Replace verbose tool outputs with compact references once their purpose is served. Tool outputs often dominate agent trajectories, so masking usually yields the largest capacity gains. The original stays retrievable.
3. **Compaction.** Summarize accumulated context at about 70% of the model's measured degradation onset (not 70% of the full window), then reinitialize with the summary. Compaction is lossy, so apply it after masking has removed the low-value bulk.
4. **Context partitioning.** Split work across sub-agents with isolated contexts when one window cannot hold the problem. Reserve this for tasks whose estimated context exceeds 60% of the window, because coordination overhead is real.

Governing principle: context quality matters more than quantity. Every optimization preserves signal while reducing noise. Measure before optimizing, then measure the optimization's effect.

## Detailed topics

### Compaction

Trigger at about 70% of the measured degradation onset (with onset at 60% of the window, that is about 42% utilization): summarize the current context, then reinitialize with the summary. Compress tool outputs first (often 80%+ of tokens), then old conversation turns, then retrieved documents. Never compress the system prompt; it anchors model behavior.

Preserve by message type:

- **Tool outputs:** key findings, metrics, error codes, conclusions. Strip verbose raw output, stack traces (unless debugging is ongoing), and boilerplate headers.
- **Conversational turns:** decisions, commitments, user preferences, context shifts. Remove filler, pleasantries, and exploratory back-and-forth already resolved.
- **Retrieved documents:** claims, facts, and data points relevant to the active task. Remove supporting evidence that served a one-time reasoning purpose.

Target 50-70% token reduction with under 5% quality degradation. If reduction exceeds 70%, audit the summary for critical information loss; over-aggressive compaction is the most common failure mode.

### Observation masking

Mask selectively by recency and ongoing relevance, not uniformly:

- **Never mask:** observations critical to the current task, from the most recent turn, used in active reasoning chains, or error outputs while debugging.
- **Mask after 3+ turns:** verbose outputs whose key points are already extracted. Replace with `[Obs:{ref_id} elided. Key: {summary}. Full content retrievable.]`
- **Mask immediately:** repeated/duplicate outputs, boilerplate headers and footers, outputs already summarized earlier.

Target 60-80% reduction in masked observations with under 2% quality impact. Keep it retrievable: store the full content externally and keep the reference ID in context.

### KV-cache optimization

Put stable content in the prefix and dynamic content at the end. When consecutive requests share an identical prefix, the cached tensors are reused, saving cost and latency.

Prompt order:

1. System prompt (most stable; never changes within a session)
2. Tool definitions
3. Frequently reused templates and few-shot examples
4. Conversation history (grows but shares a prefix with prior turns)
5. Current query and dynamic content (always last)

Remove timestamps, session counters, and request IDs from the system prompt; move dynamic metadata into a user message or tool result after the stable prefix. A single whitespace change in the prefix invalidates the cached block downstream of it. Compacting or masking earlier history also forces reprocessing of the text after it, so batch such edits and prefer edits near the end when the runtime allows. Measure cache and latency impact rather than assuming token reduction is free.

Target 70%+ cache hit rate for stable workloads (at scale, 50%+ cost and 40%+ latency reduction on cached tokens).

### Context partitioning

Partition when one context cannot hold the problem without aggressive compaction. Each sub-agent works in a clean, focused context and returns a structured result to a coordinator.

Plan partitioning when estimated task context exceeds 60% of the window. Decompose into independent subtasks, assign each to a sub-agent, and aggregate. Validate that all partitions completed before merging, merge compatible results, and summarize if the aggregate still exceeds budget.

Detailed search context stays isolated in sub-agents while the coordinator synthesizes. Coordination costs tokens (coordinator prompt, aggregation, error handling), so partition only when savings exceed that overhead.

### Budget management

Allocate explicit token budgets before the session begins: system prompt, tool definitions, retrieved documents, message history, tool outputs, and a reserved buffer (5-10% of total). Monitor against budget and trigger optimization when any category exceeds its allocation or total utilization crosses 70%.

Use trigger-based, not periodic, optimization:

- Token utilization above 80%: trigger compaction
- Attention degradation indicators (repetition, missed instructions): trigger masking + compaction
- Quality score below baseline: audit context composition before optimizing

## Practical guidance

### Decision framework

| Context composition | First action | Second action |
|---|---|---|
| Tool outputs dominate (>50%) | Observation masking | Compaction of remaining turns |
| Retrieved documents dominate | Summarization | Partitioning if docs are independent |
| Message history dominates | Compaction with selective preservation | Partitioning for new subtasks |
| Multiple components contribute | KV-cache optimization first, then layer masking + compaction | n/a |
| Near limit with active debugging | Mask resolved tool outputs only; preserve error details | n/a |

### Performance targets

- **Compaction:** 50-70% token reduction, <5% quality degradation, <10% latency overhead from the compaction step
- **Masking:** 60-80% reduction in masked observations, <2% quality impact, near-zero latency overhead
- **Cache optimization:** 70%+ hit rate for stable workloads, 50%+ cost reduction, 40%+ latency reduction
- **Partitioning:** net token savings after coordinator overhead; break-even typically needs 3+ subtasks

Iterate on measured results. If a technique does not measurably improve the target metric, remove it; optimization machinery itself costs tokens and latency.

## Examples

**Compaction trigger**

```python
if context_tokens / context_limit > 0.8:
    context = compact_context(context)
```

**Observation masking**

```python
if len(observation) > max_length:
    ref_id = store_observation(observation)
    return f"[Obs:{ref_id} elided. Key: {extract_key(observation)}]"
```

**Cache-friendly ordering**

```python
# Stable content first
context = [system_prompt, tool_definitions]  # Cacheable
context += [reused_templates]  # Reusable
context += [unique_content]  # Unique
```

**Budget-triggered policy**

```yaml
budgets:
  tool_outputs: 35%
  message_history: 30%
  retrieved_documents: 20%
  reserved_buffer: 15%
triggers:
  tool_outputs_over_budget: mask resolved observations
  total_context_over_70_percent: compact message history
  repeated_irrelevant_retrievals: tighten retrieval scope
```

## Guidelines

1. Measure before optimizing; know your current state.
2. Mask before compacting: remove low-value bulk first, then summarize what remains.
3. Design for cache stability with consistent prompts.
4. Partition before context becomes problematic.
5. Monitor effectiveness over time.
6. Balance token savings against quality preservation.
7. Test at production scale.
8. Implement graceful degradation for edge cases.

## Gotchas

1. **Whitespace breaks the KV-cache.** One whitespace or newline change in the prefix invalidates the cache from that point on. Pin system prompts as immutable strings; do not interpolate timestamps, version numbers, or session IDs. Diff prompt templates byte-for-byte between deployments.
2. **Timestamps in system prompts destroy hit rates.** `Current date: {today}` forces a full miss every day (or every request, if it includes time of day). Put dynamic metadata in a user message or tool result after the stable prefix.
3. **Compaction under pressure loses critical state.** Above ~85% utilization the summarizing model omits task goals, drops user constraints, and flattens nuance. Compact at 70-80%, not 90%+. If it must happen late, use a separate model call with a clean context containing only the material to summarize.
4. **Masking error outputs breaks debugging loops.** During active debugging (an error in the last 3 turns), suspend masking of all error-related observations until resolved.
5. **Partitioning overhead can exceed savings.** Each sub-agent needs its own system prompt, tool definitions, and coordination messages. With fewer than 3 independent subtasks the overhead often exceeds the savings. Estimate total tokens (coordinator + all sub-agents) first.
6. **Cache miss cost spikes after deployment changes.** Reordering tools, rewording the system prompt, or changing few-shot examples invalidates the prefix cache, causing a temporary 2-5x cost spike until it warms. Roll out prompt changes gradually and watch hit rate.
7. **Compaction creates false confidence in stale summaries.** A summary looks authoritative but may reflect outdated state. After compaction, re-validate it against the current task goal before proceeding.

## Related skills

If available, these cover adjacent concerns: multi-agent patterns (partitioning work across isolated contexts), evaluation (measuring whether an optimization improved quality, cost, or latency), and memory systems (persistent retrieval layers that feed context just in time).

## References

- [Context Fundamentals](./references/fundamentals.md) - window anatomy, attention mechanics and the U-shaped curve, component-by-component reference, and `scripts/context_manager.py` usage. Read when explaining context or onboarding someone.
- [Optimization Techniques](./references/optimization_techniques.md) - detailed code patterns, threshold tables, and integration examples. Read when implementing a specific technique.
- [Context Degradation](./references/degradation.md) - identifying which degradation pattern is occurring. Read when diagnosing a performance drop. [degradation-patterns.md](./references/degradation-patterns.md) holds detection code and recovery procedures, and `scripts/degradation_detector.py` runs the checks.

The `scripts/` helpers (`compaction.py`, `context_manager.py`, `degradation_detector.py`) are Python and should run in a cloud thread with a Python interpreter.
