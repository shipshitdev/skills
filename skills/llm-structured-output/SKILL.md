---
name: llm-structured-output
description: Design prompts, schemas, validation, and recovery logic for reliable machine-readable model outputs. Use when generating JSON, typed objects, extraction results, tool arguments, or any output another system must parse safely.
metadata:
  version: "1.0.0"
  tags: "llm, structured-output, json, prompt-engineering"
---

# LLM Structured Output

Build structured-output flows that are predictable enough for software to trust.

## Use This Skill For

- JSON or typed-object output from a model
- Data extraction pipelines
- Function or tool argument generation
- Prompt contracts that feed downstream automation
- Validation and retry strategies for malformed model output

## Workflow

### 1. Start With the Consumer

- Identify exactly what the downstream system needs
- Define required fields, optional fields, enums, and limits
- Keep the schema as small as possible

### 2. Make the Contract Explicit

- Provide the model with the expected structure
- State field meanings and constraints clearly
- Prefer deterministic formats over prose-plus-JSON hybrids
- If a field is free-form, bound it with type, length, or examples

### 3. Validate Everything

- Parse strictly
- Reject unknown or malformed shapes when correctness matters
- Validate enums, ranges, array sizes, and nested objects
- Treat structured output as untrusted input until validated

### 4. Design Recovery Paths

- Retry with the validation error when the output is close
- Fall back to a smaller schema if the original is too complex
- Log invalid outputs for inspection
- Avoid silent coercion that hides model mistakes

### 5. Optimize for Reliability

- Break large tasks into smaller structured steps
- Separate reasoning from final machine-readable output when needed
- Prefer schemas with stable keys and low ambiguity
- Remove optional fields that are not actually useful

## Rules

- Do not ask for markdown fences around JSON unless the consumer needs them
- Do not mix human-facing commentary into machine-facing payloads
- Prefer enums over natural-language categories
- Prefer arrays of objects over encoded strings
- Make nullability intentional, not accidental

## Common Failure Modes

- Schema too broad for the task
- Required fields that the model cannot infer
- Free-text values that should be enums
- Nested output with no examples or constraints
- Parsers that accept bad data and fail later in the pipeline

## Output

When using this skill, produce:

- The target schema or shape
- The prompt contract for generating it
- The validation and retry plan
- Any reliability risks or edge cases
