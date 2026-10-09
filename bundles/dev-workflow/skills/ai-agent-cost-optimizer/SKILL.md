---
name: ai-agent-cost-optimizer
description: Audits and cuts AI agent token and inference spend via context discipline, prompt caching, model routing, and batching. Use when AI coding bills or token waste are too high.
metadata:
  version: "2.2.5"
  tags: "ai, agents, cost, tokens, context"
when_to_use: "model tier choice, cache misses"
---

# AI Agent Cost Optimizer

Reduce AI agent spend without reducing shipped quality. Optimize for cost per correct completed task, not raw token count.

## When to Activate

- AI coding bills, token usage, API inference cost, or model spend are too high
- Reviewing agent workflows for context waste, retry loops, or cache misses
- Choosing model tiers for planning, implementation, review, or cleanup tasks
- Evaluating claims about prompt caching, cheap models, or token savings
- Capturing repeated workflows so future agents do not rediscover the same context

## Core Principle

Price the model and context to the cost of failure.

Use more capable models when a wrong answer could create expensive rework, security risk, data loss, or architectural drag. Use cheaper models and smaller context when the task is bounded, reversible, test-covered, or mechanical.

Do not save tokens in ways that increase retries, hide important evidence, or lower code quality.

## Cost Audit Workflow

### 1. Establish the Spend Shape

Identify what is actually driving cost before recommending changes:

- API versus subscription spend
- Providers and models in use
- Workflows that run most often
- Average input, output, cached input, reasoning, and tool-call tokens when available
- Retry count, failed runs, and human correction time
- Whether costs come from a few large workflows or many small calls

If usage data is unavailable, mark it unknown and inspect local configs, logs, scripts, or provider dashboards only when accessible.

### 2. Separate Verified Facts From Claims

Pricing, model availability, cache behavior, and benchmark rankings are date-sensitive. Verify current provider documentation before citing specific prices or recommending a model as the default.

Treat social posts, benchmark screenshots, and vendor marketing as hypotheses. Convert them into local tests before changing default routing.

### 3. Find Token Leaks

Look for these common waste patterns:

- Large files or directories loaded before a focused task is understood
- "Just in case" file includes
- Raw logs, build output, search output, or test output kept after the useful signal is extracted
- Tool loops that resend the same context each retry
- Repeated tool definitions or provider instructions that could be cached
- Long conversations continued after a compact summary would preserve enough state
- Premium models used for formatting, renames, lint fixes, extraction, or boilerplate
- Many small questions asked as separate calls against the same prefix
- Repeated environment discovery that should be captured as a skill, reference, or script

### 4. Reduce Context Before Switching Models

Fix context shape first:

- Search for symbols, paths, and errors before opening files
- Read the smallest relevant slice that can answer the question
- Keep stable rules, schemas, and workflow instructions in durable skills or references
- Summarize old tool outputs once their purpose is served
- Drop stale context after phase changes
- Batch read-only exploration when the questions share the same context
- Preserve exact evidence for critical debugging, security, billing, or data-loss cases

### 5. Make Cache Hits Likely

Design stable prefixes:

- Put stable instructions, tool definitions, schemas, and examples before variable task data
- Keep timestamps, session IDs, user-specific details, and retrieved snippets out of the reusable prefix
- Avoid rewriting stable instructions between calls
- Monitor cache-read and cache-write usage when provider responses expose it
- Check provider-specific thresholds, TTLs, and invalidation rules before assuming caching works

Do not generalize that streaming breaks caching. Cache misses usually come from unstable prefixes, unsupported providers or models, thresholds, TTL expiry, or changed tool/message structure.

### 6. Route by Task Risk

Use this rubric as the starting point:

| Task | Default Tier | Promote When |
|------|--------------|--------------|
| Architecture, security-critical review, irreversible operations, high-blast-radius refactors | Premium | Already premium; add review or tests |
| Feature implementation, debugging, test writing, routine refactors | Workhorse | Failing repeatedly, weak tests, or hidden architecture risk |
| Lint, format, rename, simple extraction, boilerplate, classification | Utility or local | Output needs nuanced judgment or affects production behavior |
| Long agentic loops | Workhorse with strict context budgets | Loop reaches unclear design decisions or persistent failures |
| Exploration across unknown codebases | Workhorse or premium for initial map, then cheaper tier for bounded follow-up | Architecture is unclear or stakes are high |

Use local evaluation over broad leaderboard claims. A cheaper model that doubles retries may be more expensive than the premium model.

### 7. Batch and Partition Deliberately

Batch related small questions into one call when they share context. Partition broad tasks into independent subtasks when each subtask can run with isolated context and return a compact result.

Avoid spawning extra agents just to parallelize trivial work. Multi-agent systems can increase token spend unless context isolation or wall-clock savings justify the overhead.

### 8. Capture Repeated Workflows

When a workflow is repeated and stable, capture it so agents stop rediscovering it:

- Write a focused skill for multi-step procedural knowledge
- Move long background material into references loaded only when needed
- Create deterministic scripts for fragile or repeated transformations
- Keep environment facts in repo memory or project docs with verification dates

Capture the final working workflow, not the exploratory path that found it.

### 9. Measure the Result

Compare before and after using task-level metrics:

- Cost per completed task
- Input, output, cached input, and tool-call tokens
- Cache hit rate
- Retry count
- Wall-clock time
- Test pass rate or review defect rate
- Human correction time

Report savings as measured ranges. Avoid unsupported claims like "80% reduction" unless the baseline and after-state are both known.

## Output Format

When auditing a workflow, return:

1. **Top Leaks** - Ordered by likely spend impact
2. **Low-Risk Fixes** - Changes that reduce cost without quality risk
3. **Routing Changes** - Model-tier changes and promotion conditions
4. **Caching Plan** - Stable prefix, variable suffix, and metrics to watch
5. **Capture Candidates** - Workflows worth turning into skills, references, or scripts
6. **Unverified Claims** - Pricing or model-quality claims that need current source checks

## Guardrails

- Do not recommend a specific provider or model as default without current pricing and local quality evidence
- Do not remove context required for correctness, safety, compliance, or auditability
- Do not optimize mechanical token count if it increases retries or review burden
- Do not treat prompt caching as magic; validate cache hits in usage data
- Do not encode volatile price tables as enduring skill content
- Do not use editing shortcuts that violate the repository's established workflow

## Integration

Related skills:

- `context-optimization` (`references/fundamentals.md`) - Understand what consumes context
- `context-optimization` - Apply compaction, masking, caching, and partitioning
- `multi-agent-patterns` - Evaluate when sub-agent context isolation is worth the overhead
- `tool-design` - Reduce tool ambiguity and response bloat
- `skill-capture` - Persist repeated workflows as reusable skills
