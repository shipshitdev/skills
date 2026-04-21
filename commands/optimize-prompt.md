# Optimize Prompt (Lyra-Inspired)

Transform vague prompts into precision-crafted, effective AI prompts using systematic optimization.

## When to Use

- Optimizing AI generation prompts (content, images, code)
- Improving prompt templates in services or pipelines
- Creating better system prompts
- Debugging poor AI responses

## The 4-D Optimization Framework

### 1. DECONSTRUCT

Extract core elements:

- Core intent: What's the goal?
- Key entities: What are we working with?
- Context: What background info matters?
- Output format: What should the result look like?
- Constraints: What are the limitations?
- Missing info: What's unclear?

**Example:**

```
INPUT: "Write me a post about AI"

DECONSTRUCT:
- Intent: Generate social media content
- Entity: AI topic (vague)
- Context: Missing (platform? audience? tone?)
- Output: Social media post (which platform?)
- Constraints: Unknown (length? style?)
- Missing: Platform, audience, key message, tone
```

### 2. DIAGNOSE

Audit for issues:

- **Clarity:** Is intent clear?
- **Specificity:** Are requirements concrete?
- **Completeness:** Is all needed info present?
- **Structure:** Is prompt well-organized?
- **Complexity:** Does it match task difficulty?

Common issues: vague terms ("make it good"), missing context, no examples, poor structure.

### 3. DEVELOP

Select techniques based on task type:

**Creative tasks:** role assignment, tone emphasis, audience specification, examples, brand voice constraints.

**Technical tasks:** constraint-based, step-by-step structure, error handling specs, output format specification.

**Complex requests:** chain-of-thought, systematic frameworks, subtask decomposition, validation steps.

### 4. DELIVER

Construct optimized prompt:

```markdown
## Role & Context
[Who the AI should act as and what context matters]

## Task
[Clear, specific description]

## Requirements
- [Specific requirement 1]
- [Specific requirement 2]

## Constraints
- [Limitation 1]
- [Limitation 2]

## Output Format
[Exactly how the result should be structured]

## Examples (if applicable)
[Show, don't just tell]
```

## Key Techniques

### Role Assignment

```
BAD:  "Write a tweet"
GOOD: "You are a social media expert specializing in tech content for B2B SaaS."
```

### Context Layering

```
BAD:  "Create a post about our product"
GOOD: "Create a LinkedIn post about our AI tool. Target: Marketing teams at SMBs. Key benefit: Save 10 hours/week."
```

### Output Specification

```
BAD:  "Make it short"
GOOD: "150-200 characters. Include 2-3 hashtags. End with a call-to-action question."
```

### Chain-of-Thought

```
"Before writing:
1. Identify the core message (1 sentence)
2. List 3 supporting points
3. Choose the most compelling hook
4. Write the post following this structure"
```

### Few-Shot Learning

Provide 2-3 examples of desired output format and quality level before the actual request.

## Platform-Specific Notes

### Claude (Anthropic)

- Handles long context well (200K tokens)
- Excels at multi-step reasoning
- Be explicit about format and success criteria
- Supports XML tags for structure

### OpenAI (GPT-4)

- Structured sections with headers work well
- Clear role definitions
- May lose focus on very long prompts

### Image Models

- Detailed visual descriptions
- Style and composition specs
- Negative prompts (what to avoid)

## Quick Checklist

```
- [ ] Clear role/persona defined
- [ ] Specific task description
- [ ] Context provided
- [ ] Output format specified
- [ ] Constraints listed
- [ ] Examples included (if helpful)
- [ ] Quality criteria defined
```

## Workflow

1. **Identify** current prompt
2. **Apply** 4-D framework
3. **Test** optimized version
4. **Compare** output quality
5. **Iterate** if needed

---

Inspired by: claudecodecommands.directory/Lyra
