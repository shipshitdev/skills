---
name: ai-loading-ux
description: "Designs AI waiting-state UX: thinking indicators, reasoning display, progress steps, and streaming states. Use when asked to improve loading or perceived wait in AI interfaces."
metadata:
  version: "2.2.4"
  tags: "ai, loading, ux"
when_to_use: "chain-of-thought display"
---

# AI Loading UX

Design patterns for showing users what is happening while they wait for AI output.

## Decision framework

First identify which pattern category applies:

| User is waiting for... | Pattern category | Key goal |
|------------------------|------------------|----------|
| AI reasoning/thinking | **Reasoning Display** | Build trust through transparency |
| Multi-step task completion | **Progress Steps** | Show advancement toward goal |
| Content generation/streaming | **Streaming States** | Reduce perceived wait time |
| Background processing | **Status Indicators** | Confirm work is happening |

## Core principles

1. **The elevator mirror effect.** Waiting for AI feels slower. Give users something to watch or read; animated indicators reduce perceived wait even when actual time is unchanged.
2. **Progressive disclosure.** Show a condensed indicator by default ("Thinking..."), make details available but not forced, and let curious users expand.
3. **More transparency is not better UX.** Users want answers, but they want to trust the answer came from good reasoning.
4. **Signal completion clearly.** Ambiguous end states frustrate users.

## Pattern quick reference

### Reasoning display (chain-of-thought)

For when the AI is "thinking" through a problem. See [references/reasoning-patterns.md](references/reasoning-patterns.md).

Best approach (Claude-style):

- Hidden by default, expandable on demand
- Structured bullets when expanded
- Time counter or progress indicator
- Clear "done" state

Anti-patterns:

- Wall of streaming text (overwhelming)
- Scrolling too fast to read
- No expand option (feels opaque)
- No clear end state

### Progress steps

For sequential tasks. See [references/progress-patterns.md](references/progress-patterns.md).

- Show current step and total steps
- Mark completed steps visually
- Show what is actively happening
- Allow step-level details on expand

### Streaming states

For token-by-token generation. See [references/streaming-patterns.md](references/streaming-patterns.md).

- Typing cursor or text animation
- Smooth token appearance (not jarring)
- Skeleton for the expected content shape
- "Stop generating" escape hatch

### Status indicators

For background work. See [references/status-patterns.md](references/status-patterns.md).

- Subtle but visible animation
- Brief description of the current action
- Do not block the user from other actions
- Notify on completion

## Implementation checklist

For any AI loading state:

1. [ ] Identify the pattern category from the decision framework.
2. [ ] Choose the visibility level: always visible, expandable, or minimal.
3. [ ] Add motion: animation reduces perceived wait (keep it subtle).
4. [ ] Show progress: time elapsed, steps completed, or content streamed.
5. [ ] Signal completion with a clear visual/state change.
6. [ ] Provide an escape: stop/cancel for long operations.
7. [ ] Handle errors: never leave the user in a permanent loading state.
8. [ ] Test on slow connections for graceful degradation.

## Product comparisons (reference; products change, verify against current behavior)

| Product | Approach | Strength | Weakness |
|---------|----------|----------|----------|
| Claude | Hidden reasoning, expandable, structured bullets | Low cognitive load | Can feel opaque |
| ChatGPT | Brief labels, auto-collapse | Unobtrusive | Less transparent |
| DeepSeek | Full streaming reasoning | Maximum transparency | Overwhelming |
| Gemini | User-scrolled, numbered steps | Clear structure | Unclear completion |

## References

Read the file for your pattern category:

- [references/reasoning-patterns.md](references/reasoning-patterns.md): chain-of-thought, thinking indicators
- [references/progress-patterns.md](references/progress-patterns.md): step sequences, task completion
- [references/streaming-patterns.md](references/streaming-patterns.md): token streaming, content generation
- [references/status-patterns.md](references/status-patterns.md): background processing, polling states
