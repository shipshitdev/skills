<!-- Upstream: muratcankoylan/Agent-Skills-for-Context-Engineering
skills/context-fundamentals @ cbc2c978133d (MIT, synced 2026-06-12). Folded into
`context-optimization` on 2026-10-03 (#168), with its context-components reference
appended. The helper script now lives at ../scripts/context_manager.py. -->

# Context Engineering Fundamentals

Context is the complete state available to a language model at inference time: system instructions, tool definitions, retrieved documents, message history, and tool outputs. Context engineering is the discipline of curating the smallest high-signal token set that maximizes the likelihood of desired outcomes.

## Core Concepts

Treat context as a finite attention budget, not a storage bin. Every token added competes for the model's attention and depletes a budget that cannot be refilled mid-inference. The engineering problem is maximizing utility per token against three constraints: the hard token limit, the softer effective-capacity ceiling, and the U-shaped attention curve that penalizes information placed in the middle of context (claim-context-degradation-lost-middle-ruler).

Apply four principles when assembling context:

1. **Informativity over exhaustiveness** — include only what matters for the current decision; design systems that can retrieve additional information on demand.
2. **Position-aware placement** — place critical constraints at the beginning and end of context because long-context evaluations show middle-position information is less reliably recovered than edge-position information (claim-context-degradation-lost-middle-ruler).
3. **Progressive disclosure** — load skill names and summaries at startup; load full content only when a skill activates for a specific task.
4. **Iterative curation** — context engineering is not a one-time prompt-writing exercise but an ongoing discipline applied every time content is passed to the model.

## Detailed Topics

### The Anatomy of Context

**System Prompts**
Organize system prompts into distinct sections using XML tags or Markdown headers (background, instructions, tool guidance, output format). System prompts persist throughout the conversation, so place the most critical constraints at the beginning and end where attention is strongest.

Calibrate instruction altitude to balance two failure modes. Too-low altitude hardcodes brittle logic that breaks when conditions shift. Too-high altitude provides vague guidance that fails to give concrete signals for desired behavior. Aim for heuristic-driven instructions: specific enough to guide behavior, flexible enough to generalize — for example, numbered steps with room for judgment at each step.

Start minimal, then add instructions reactively based on observed failure modes rather than preemptively stuffing edge cases. Curate diverse, canonical few-shot examples that portray expected behavior instead of listing every possible scenario.

**Tool Definitions**
Write tool descriptions that answer three questions: what the tool does, when to use it, and what it returns. Include usage context, parameter defaults, and error cases — agents cannot disambiguate tools that a human engineer cannot disambiguate either.

Keep the tool set minimal. Consolidate overlapping tools because bloated tool sets create ambiguous decision points and consume disproportionate context after JSON serialization (tool schemas typically inflate 2-3x compared to equivalent plain-text descriptions).

**Retrieved Documents**
Maintain lightweight identifiers (file paths, stored queries, web links) and load data into context dynamically using just-in-time retrieval. This mirrors human cognition — maintain an index, not a copy. Strong identifiers (e.g., `customer_pricing_rates.json`) let agents locate relevant files even without search tools; weak identifiers (e.g., `data/file1.json`) force unnecessary loads.

When chunking large documents, split at natural semantic boundaries (section headers, paragraph breaks) rather than arbitrary character limits that sever mid-concept.

**Message History**
Message history serves as the agent's scratchpad memory for tracking progress, maintaining task state, and preserving reasoning across turns. For long-running tasks, it can grow to dominate context usage — monitor and apply compaction before it crowds out active instructions.

Cyclically refine history: once a tool has been called deep in the conversation, the raw result rarely needs to remain verbatim. Replace stale tool outputs with compact summaries or references to reduce low-signal bulk.

**Tool Outputs**
Tool outputs often dominate context in agent trajectories (claim-context-optimization-tool-output-dominance). Apply observation masking: replace verbose outputs with compact references once the agent has processed the result. Retain only the most recently relevant file contents; compress or evict older ones.

### Context Windows and Attention Mechanics

**The Attention Budget**
For n tokens, the attention mechanism computes n-squared pairwise relationships. As context grows, the model's ability to maintain these relationships degrades — not as a hard cliff but as a performance gradient. Models trained predominantly on shorter sequences have fewer specialized parameters for context-wide dependencies, creating an effective ceiling well below the nominal window size.

Design for this gradient: assume effective capacity is materially below the advertised window until measured on the target workload. Large nominal context windows do not remove the need for task-specific degradation tests (claim-context-degradation-lost-middle-ruler).

**Position Encoding Limits**
Position encoding interpolation extends sequence handling beyond training lengths but introduces degradation in positional precision. Expect reduced accuracy for information retrieval and long-range reasoning at extended contexts compared to performance on shorter inputs.

**Progressive Disclosure in Practice**
Implement progressive disclosure at three levels:

1. **Skill selection** — load only names and descriptions at startup; activate full skill content on demand.
2. **Document loading** — load summaries first; fetch detail sections only when the task requires them.
3. **Tool result retention** — keep recent results in full; compress or evict older results.

Keep the boundary crisp: if a skill or document is activated, load it fully rather than partially — partial loads create confusing gaps that degrade reasoning quality.

### Context Quality Versus Quantity

Reject the assumption that larger context windows solve memory problems. Processing cost grows disproportionately with context length — not just linear cost scaling, but degraded model performance beyond effective capacity thresholds. Long inputs remain expensive even with prefix caching.

Apply the signal-density test: for each piece of context, ask whether removing it would change the model's output. If not, remove it. Redundant content does not merely waste tokens — it actively dilutes attention from high-signal content.

## Practical Guidance

This section provides conceptual application advice. Pointers to operational skills are explicit.

### Reasoning About a Context Decision

When a context-related design decision needs to be made, separate the conceptual question from the operational one. The conceptual question is "what does this mean and why does it matter"; the operational question is "what specific technique do we apply." Use this skill to answer the first; route to the specialized skill that owns the second.

For example, deciding whether to summarize a long agent session has two parts: (1) why summarization is needed at all (attention budget is finite, U-shaped curve degrades middle content, signal density matters more than volume - this skill) and (2) what compaction strategy preserves the right state and at what utilization threshold to trigger it (route to the operational skill that owns session compaction).

### Reading Order For New Contributors

A contributor coming to context engineering for the first time should read:

1. This skill, to internalize the attention-budget framing and the U-shaped curve.
2. `context-degradation`, to see what context failures look like in practice and how to diagnose them.
3. Two or three of `context-optimization`, `memory-systems` depending on which operational concern is most relevant to their project.

Skipping step 1 produces operators who apply techniques without understanding why; skipping the operational skills produces theorists who do not know which technique fits which failure mode.

## Examples

**Example 1: Organizing System Prompts**

Illustrates the conceptual point that critical constraints belong at attention-favored positions (beginning and end), and that explicit section boundaries help the model parse the prompt:

```markdown
<BACKGROUND_INFORMATION>
You are a Python expert helping a development team.
Current project: Data processing pipeline in Python 3.9+
</BACKGROUND_INFORMATION>

<INSTRUCTIONS>
- Write clean, idiomatic Python code
- Include type hints for function signatures
- Add docstrings for public functions
- Follow PEP 8 style guidelines
</INSTRUCTIONS>

<OUTPUT_DESCRIPTION>
Provide code blocks with syntax highlighting.
Explain non-obvious decisions in comments.
</OUTPUT_DESCRIPTION>
```

**Example 2: The Attention Budget As A Mental Model**

A large-context model does not have an equally attended context. Effective capacity is workload-specific, and the U-shaped curve penalizes information placed in the middle. When deciding how much of an upstream knowledge base to load, this is the mental model: do not ask "will it fit," ask "will the model still attend to the parts that matter."

The corresponding operational question (which technique should reduce the load) belongs to `context-optimization`.

## Guidelines

1. Treat context as a finite resource with diminishing returns
2. Place critical information at attention-favored positions (beginning and end)
3. Use progressive disclosure to defer loading until needed
4. Organize system prompts with clear section boundaries
5. Monitor context usage during development
6. Implement compaction triggers at 70-80% utilization
7. Design for context degradation rather than hoping to avoid it
8. Prefer smaller high-signal context over larger low-signal context

## Gotchas

1. **Nominal window is not effective capacity**: A model advertising a large context window may degrade well before that limit on complex retrieval or reasoning tasks. Budget below the nominal window until your own degradation tests prove otherwise.

2. **Character-based token estimates silently drift**: The ~4 characters/token heuristic for English prose breaks down for code (2-3 chars/token), URLs and file paths (each slash, dot, and colon is a separate token), and non-English text (often 1-2 chars/token). Use the provider's actual tokenizer (e.g., tiktoken for OpenAI models, Anthropic's token counting API) for any budget-critical calculation.

3. **Tool schemas inflate 2-3x after JSON serialization**: A tool definition that looks compact in source code expands significantly when serialized — brackets, quotes, colons, and commas each consume tokens. Ten tools with moderate schemas can consume 5,000-8,000 tokens before a single message is sent. Audit serialized tool token counts, not source-code line counts.

4. **Message history balloons silently in agentic loops**: Each tool call adds both the request and the full response to history. After 20-30 iterations, history can consume 70-80% of the window while the agent shows no visible symptoms until reasoning quality collapses. Set a hard token ceiling on history and trigger compaction proactively.

5. **Critical instructions in the middle get lost**: The U-shaped attention curve means the middle of context receives 10-40% less recall accuracy than the beginning and end. Never place safety constraints, output format requirements, or behavioral guardrails in the middle of a long system prompt — anchor them at the top or bottom.

6. **Progressive disclosure that loads too eagerly defeats its purpose**: Loading every "potentially relevant" skill or document at the first hint of relevance recreates the context-stuffing problem. Set strict activation thresholds — a skill should load only when the task explicitly matches its trigger conditions, not when the topic is merely adjacent.

7. **Mixing instruction altitudes causes inconsistent behavior**: Combining hyper-specific rules ("always use exactly 3 bullet points") with vague directives ("be helpful") in the same prompt creates conflicting signals. Group instructions by altitude level and keep each section internally consistent — either heuristic-driven or prescriptive, not both interleaved.

## Integration

This skill is the conceptual foundation. It does not own operational work; it provides the mental models the operational skills assume.

Routing map for operational work:

- `context-degradation`: diagnosing attention failures, lost-in-middle, poisoning, distraction.
- `context-optimization`: token-efficiency tactics (masking, partitioning, caching, budgets).
- `memory-systems`: cross-session memory architectures with entity tracking.
- `multi-agent-patterns`: when to split work across agents for context isolation.
- `tool-design`: writing tool descriptions and schemas that route correctly.

Read this skill first to build the mental models; read the operational skill that fits the task when actually doing the work.

## Context Components (reference)

This document provides detailed technical reference for each context component in agent systems.

### System Prompt Engineering

#### Section Structure

Organize system prompts into distinct sections with clear boundaries. A recommended structure:

```
<BACKGROUND_INFORMATION>
Context about the domain, user preferences, or project-specific details
</BACKGROUND_INFORMATION>

<INSTRUCTIONS>
Core behavioral guidelines and task instructions
</INSTRUCTIONS>

<TOOL_GUIDANCE>
When and how to use available tools
</TOOL_GUIDANCE>

<OUTPUT_DESCRIPTION>
Expected output format and quality standards
</OUTPUT_DESCRIPTION>
```

This structure allows agents to locate relevant information quickly and enables selective context loading in advanced implementations.

#### Altitude Calibration

The "altitude" of instructions refers to the level of abstraction. Consider these examples:

**Too Low (Brittle):**

```
If the user asks about pricing, check the pricing table in docs/pricing.md.
If the table shows USD, convert to EUR using the exchange rate in
config/exchange_rates.json. If the user is in the EU, add VAT at the
applicable rate from config/vat_rates.json. Format the response with
the currency symbol, two decimal places, and a note about VAT.
```

**Too High (Vague):**

```
Help users with pricing questions. Be helpful and accurate.
```

**Optimal (Heuristic-Driven):**

```
For pricing inquiries:
1. Retrieve current rates from docs/pricing.md
2. Apply user location adjustments (see config/location_defaults.json)
3. Format with appropriate currency and tax considerations

Prefer exact figures over estimates. When rates are unavailable,
say so explicitly rather than projecting.
```

The optimal altitude provides clear steps while allowing flexibility in execution.

### Tool Definition Specification

#### Schema Structure

Each tool should define:

```python
{
    "name": "tool_function_name",
    "description": "Clear description of what the tool does and when to use it",
    "parameters": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "What this parameter controls",
                "default": "reasonable_default_value"
            }
        },
        "required": ["param_name"]
    },
    "returns": {
        "type": "object",
        "description": "What the tool returns and its structure"
    }
}
```

#### Description Engineering

Tool descriptions should answer: what the tool does, when to use it, and what it produces. Include usage context, examples, and edge cases.

**Weak Description:**

```
Search the database for customer information.
```

**Strong Description:**

```
Retrieve customer information by ID or email.

Use when:
- User asks about a specific customer's details, history, or status
- User provides a customer identifier and needs related information

Returns customer object with:
- Basic info (name, email, account status)
- Order history summary
- Support ticket count

Returns null if customer not found. Returns error if database unreachable.
```

### Retrieved Document Management

#### Identifier Design

Design identifiers that convey meaning and enable efficient retrieval:

**Poor identifiers:**

- `data/file1.json`
- `ref/ref.md`
- `2024/q3/report`

**Strong identifiers:**

- `customer_pricing_rates.json`
- `engineering_onboarding_checklist.md`
- `2024_q3_revenue_report.pdf`

Strong identifiers allow agents to locate relevant files even without search tools.

#### Document Chunking Strategy

For large documents, chunk strategically to preserve semantic coherence:

```python
# Pseudocode for semantic chunking
def chunk_document(content):
    """Split document at natural semantic boundaries."""
    boundaries = find_section_headers(content)
    boundaries += find_paragraph_breaks(content)
    boundaries += find_logical_breaks(content)
    
    chunks = []
    for i in range(len(boundaries) - 1):
        chunk = content[boundaries[i]:boundaries[i+1]]
        if len(chunk) > MIN_CHUNK_SIZE and len(chunk) < MAX_CHUNK_SIZE:
            chunks.append(chunk)
    
    return chunks
```

Avoid arbitrary character limits that split mid-sentence or mid-concept.

### Message History Management

#### Turn Representation

Structure message history to preserve key information:

```python
{
    "role": "user" | "assistant" | "tool",
    "content": "message text",
    "reasoning": "optional chain-of-thought",
    "tool_calls": [list if role="assistant"],
    "tool_output": "output if role="tool"",
    "summary": "compact summary if conversation is long"
}
```

#### Summary Injection Pattern

For long conversations, inject summaries at intervals:

```python
def inject_summaries(messages, summary_interval=20):
    """Inject summaries at regular intervals to preserve context."""
    summarized = []
    for i, msg in enumerate(messages):
        summarized.append(msg)
        if i > 0 and i % summary_interval == 0:
            summary = generate_summary(summarized[-summary_interval:])
            summarized.append({
                "role": "system",
                "content": f"Conversation summary: {summary}",
                "is_summary": True
            })
    return summarized
```

### Tool Output Optimization

#### Response Formats

Provide response format options to control token usage:

```python
def get_customer_response_format():
    return {
        "format": "concise | detailed",
        "fields": ["id", "name", "email", "status", "history_summary"]
    }
```

The concise format returns essential fields only; detailed returns complete objects.

#### Observation Masking

For verbose tool outputs, consider masking patterns:

```python
def mask_observation(output, max_length=500):
    """Replace long observations with compact references."""
    if len(output) <= max_length:
        return output
    
    reference_id = store_observation(output)
    return f"[Previous observation elided. Full content stored at reference {reference_id}]"
```

This preserves information access while reducing token usage.

### Context Budget Estimation

#### Token Counting Approximation

For planning purposes, estimate tokens at approximately 4 characters per token for English text:

```
1000 words ≈ 7500 characters ≈ 1800-2000 tokens
```

This is a rough approximation; actual tokenization varies by model and content type.

#### Context Budget Allocation

Allocate context budget across components:

| Component | Typical Range | Notes |
|-----------|---------------|-------|
| System prompt | 500-2000 tokens | Stable across session |
| Tool definitions | 100-500 per tool | Grows with tool count |
| Retrieved documents | Variable | Often largest consumer |
| Message history | Variable | Grows with conversation |
| Tool outputs | Variable | Can dominate context |

Monitor actual usage during development to establish baseline allocations.

### Progressive Disclosure Implementation

#### Skill Activation Pattern

```python
def activate_skill_context(skill_name, task_description):
    """Load skill context when task matches skill description."""
    skill_metadata = load_all_skill_metadata()
    
    relevant_skills = []
    for skill in skill_metadata:
        if skill_matches_task(skill, task_description):
            relevant_skills.append(skill)
    
    # Load full content only for most relevant skills
    for skill in relevant_skills[:MAX_CONCURRENT_SKILLS]:
        skill_context = load_skill_content(skill)
        inject_into_context(skill_context)
```

#### Reference Loading Pattern

```python
def get_reference(file_reference):
    """Load reference file only when explicitly needed."""
    if not file_reference.is_loaded:
        file_reference.content = read_file(file_reference.path)
        file_reference.is_loaded = True
    return file_reference.content
```

This pattern ensures files are loaded once and cached for the session.
