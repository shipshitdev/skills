---
description: "Optimize a prompt or prompt template, or debug why an AI response is poor."
argument-hint: "[path]"
disable-model-invocation: true
---

# Prompt - Optimize a Prompt

Transform a vague prompt into a precision-crafted one — for AI generation,
prompt templates in services or pipelines, or system prompts — or debug why an
AI response is poor.

## Usage

```bash
/prompt              # optimize the prompt you provide or point at
/prompt <path>       # optimize a prompt template file in the codebase
```

`/prompt help` prints this Usage block and stops without running anything.

## Workflow

Use the `prompt-engineering` skill, following its 4-D optimization workflow
(`references/prompt-optimization.md`): Deconstruct the prompt's intent and
gaps, Diagnose clarity/specificity/structure issues, Develop the right
techniques for the task type, and Deliver the rebuilt prompt.

1. **Identify** the prompt to optimize — provided inline, or read from the
   file/service the user points at.
2. **Apply** the 4-D framework and the skill's technique catalog (role
   assignment, context layering, output specification, few-shot examples,
   chain-of-thought).
3. **Return** the optimized prompt with a short note on what changed and why,
   plus how to A/B it against the original.

## Gates

- Rewrites are proposals: show the optimized prompt; only edit a template file
  in place when the user asked for the edit.
