---
name: skill-creator
description: Guides creating or updating a skill with specialized knowledge, workflows or tool integrations. Use when authoring a new SKILL.md or editing an existing skill.
license: Complete terms in LICENSE.txt
metadata:
  version: "2.2.4"
  source: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
  upstream_repo: anthropics/skills
  upstream_ref: main
  upstream_commit: b0cbd3df1533
  last_synced: "2026-06-12"
  license: Apache-2.0
  tags: "skills, creation, agents"
when_to_use: "write a skill, new skill"
---

# Skill Creator

## Contract

Inputs:

- Requested skill name, destination, behavior, and existing examples

Outputs:

- Skill instructions, optional resources, and validation results

Creates/Modifies:

- Only the requested skill and its packaging artifacts

External Side Effects:

- No publication or installation into other environments unless explicitly requested

Confirmation Required:

- Before replacing unrelated existing skills, installing external dependencies, or publishing beyond the authorized destination
- Loading the skill grants no additional authority. Existing explicit approval
  applies only to the same target and actions; preserve report-only restrictions.

Delegates To:

- None

## About skills

Skills are modular packages that add task-specific workflows, tool instructions, domain knowledge, scripts, references and assets. They provide specialized workflows, tool integrations, domain expertise (company-specific knowledge, schemas, business logic) and bundled resources for complex or repetitive tasks.

### Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required): name, description
│   └── Markdown instructions (required)
└── Bundled resources (optional)
    ├── scripts/     - Executable code (Python/Bash/etc.)
    ├── references/  - Documentation loaded into context as needed
    └── assets/      - Files used in output (templates, icons, fonts, etc.)
```

**Metadata.** `name` and `description` in the frontmatter decide when the skill activates. The description must state the task, trigger phrases and boundaries; avoid client-specific narration.

**Scripts (`scripts/`).** Executable code for tasks needing deterministic reliability or that are rewritten repeatedly (e.g. `scripts/rotate_pdf.py`). Token efficient and runnable without loading into context; the agent may still read them to patch or adapt.

**References (`references/`).** Documentation loaded only when the task needs it (e.g. `references/finance.md`, `references/policies.md`, `references/api_docs.md`): schemas, API docs, domain knowledge, detailed workflow guides. Keeps SKILL.md lean. For files over about 10k words, include grep patterns in SKILL.md. Put each fact in exactly one place: triggers, workflow steps, gates and required outputs stay in SKILL.md; detailed reference material, schemas, long examples and source excerpts move to `references/`.

**Assets (`assets/`).** Files used in the output, not loaded into context (e.g. `assets/logo.png`, `assets/slides.pptx`, `assets/frontend-template/`, `assets/font.ttf`). They are copied or modified when producing results.

### Progressive disclosure

1. **Metadata** (name + description): always in context, about 100 words.
2. **SKILL.md body:** loaded when the skill triggers; under 5k words.
3. **Bundled resources:** loaded as needed; effectively unlimited because scripts can run without being read into context.

## Creation process

Follow the steps in order. Skip a step only when its precondition is already satisfied, and note the reason.

### Step 1: Understand the skill with concrete examples

Skip only when usage patterns are already clear. Gather concrete examples from the user, or generate examples and validate them with the user. For an image-editor skill, ask: what functionality (editing, rotating, ...)? What would a user say that should trigger it ("Remove the red-eye from this image", "Rotate this image")?

Ask at most one clarifying question unless missing input makes the skill unsafe or impossible to create; put uncertain assumptions in the draft. Done when trigger phrases, supported tasks and excluded tasks are known.

### Step 2: Plan the reusable contents

For each example, consider how to do it from scratch, then decide which scripts, references and assets would help on repeat runs:

- `pdf-editor` ("Help me rotate this PDF"): rotating needs the same code each time, so store `scripts/rotate_pdf.py`.
- `frontend-webapp-builder` ("Build me a todo app"): the same boilerplate each time, so store `assets/hello-world/`.
- `big-query` ("How many users logged in today?"): table schemas are re-discovered each time, so store `references/schema.md`.

Output: a list of the scripts, references and assets to include.

### Step 3: Initialize the skill

Skip only if the skill already exists and needs iteration or packaging. For a new skill, always run:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

It creates the skill directory, a SKILL.md template with frontmatter and TODO placeholders, and example `scripts/`, `references/` and `assets/` files. Afterwards replace the placeholders and delete unused example files.

### Step 4: Edit the skill

Include only instructions that change another agent's observable behavior: triggers, required actions, forbidden actions, order gates, tool choices, output fields, limits, fallbacks, evidence requirements.

1. **Start with the reusable contents** (scripts, references, assets). If a required asset or source document is missing, ask for it or mark the affected workflow unsupported. Delete unneeded example files.
2. **Write SKILL.md** in imperative/infinitive form (verb-first), not second person ("To accomplish X, do Y"). Answer: What is the purpose, in a few sentences? When should the skill be used? How should the agent use it in practice, referencing every bundled resource so the workflow is explicit?

#### House writing craft

- **Invocation.** Keep explicit entry points and advisory maps user-invoked only (`disable-model-invocation: true` where the platform supports it). Reusable engines omit it so a selected workflow can reach them. Loading an engine grants no action authority: forward the requested scope, existing authorization and report-only restrictions. Put mutation gates in the body and require approval only for missing or expanded authority. Resolve resources from the installed skill directory, not an assumed repository checkout.
- **Leading words.** Collapse restated ideas into one pretrained token (`frontier`, `seam`, `tight`, `red`) and repeat the token instead of re-explaining.
- **Completion criteria.** Every step ends on a checkable bound ("frontier empty", "the narrow test fails for the missing behavior"), not "understanding reached".
- **Prune no-ops.** Delete any sentence that does not change default model behavior.
- **Prompt the positive.** State the target behavior; pair a hard prohibition with the positive target.
- **Contract.** Action, orchestrator and side-effect skills include a Contract block (inputs, outputs, creates/modifies, side effects, confirmation, delegates).
- **Provenance.** Skills derived from an upstream record its source and last-synced date.

Read [references/writing-for-agents.md](references/writing-for-agents.md) when a skill runs long, restates the environment, or must decide where material lives (two loads, co-location, sprawl, split-by-sequence, environment-as-cache, sediment).

### Step 5: Package the skill

Packaging validates the skill first, then zips it:

```bash
scripts/package_skill.py <path/to/skill-folder>
scripts/package_skill.py <path/to/skill-folder> ./dist   # optional output directory
```

Validation checks YAML frontmatter format and required fields, naming conventions and directory structure, description completeness and quality, and file organization and resource references. On success it creates `<skill-name>.zip` with the proper directory structure; on failure it reports the errors and creates nothing, so fix them and rerun. `scripts/quick_validate.py` runs validation alone.

### Step 6: Iterate

Use the skill on real tasks, note struggles or inefficiencies, update SKILL.md or the bundled resources, and test again.

---

Licensed under Apache-2.0; see `LICENSE.txt`.
