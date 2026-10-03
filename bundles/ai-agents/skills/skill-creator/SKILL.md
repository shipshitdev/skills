---
name: skill-creator
description: Guide for creating effective skills. Use when creating a new skill or updating an existing one to extend agent capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
metadata:
  version: "2.2.2"
  source: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
  upstream_repo: anthropics/skills
  upstream_ref: main
  upstream_commit: b0cbd3df1533
  last_synced: "2026-06-12"
  license: Apache-2.0
  tags: "skills, creation, agents"
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

## About Skills

Skills are modular packages that add task-specific workflows, tool instructions,
domain knowledge, scripts, references, and assets.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

**Metadata:** The `name` and `description` in YAML frontmatter determine when
the skill is activated. The description must include the task, trigger phrases,
and boundaries; avoid client-specific narration.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by the agent for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material loaded only when required by the current
task.

- **When to include**: For documentation the agent should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when the agent determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Put each fact in exactly one place. Keep triggers,
  workflow steps, gates, and required outputs in SKILL.md. Move detailed
  reference material, schemas, long examples, and source excerpts to
  `references/`.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output the agent produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables the agent to use files without loading them into context

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by the agent (Unlimited*)

*Unlimited because scripts can be executed without reading into context window.

## Skill Creation Process

Follow the "Skill Creation Process" in order. Skip a step only when its
precondition is already satisfied and note the reason.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

Ask at most one clarifying question unless missing input makes the skill unsafe
or impossible to create. Put uncertain assumptions in the draft.

Conclude this step when trigger phrases, supported tasks, and excluded tasks are
known.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script.
The script generates the required directory, frontmatter, and resource folders.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, replace the generated SKILL.md placeholders and delete any
unused example files.

### Step 4: Edit the Skill

When editing the skill, include only instructions that change another agent's
observable behavior: triggers, required actions, forbidden actions, order gates,
tool choices, output fields, limits, fallbacks, or evidence requirements.

#### Start with Reusable Skill Contents

Start implementation with the reusable resources identified above: `scripts/`,
`references/`, and `assets/`. If a required asset or source document is missing,
ask for that item or mark the affected workflow unsupported.

Also, delete any example files and directories not needed for the skill. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update SKILL.md

**Writing Style:** Write the entire skill using **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language (e.g., "To accomplish X, do Y" rather than "You should do X" or "If you need to do X"). This maintains consistency and clarity for AI consumption.

To complete SKILL.md, answer the following questions:

1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used?
3. In practice, how should the agent use the skill? Reference all reusable skill contents developed above so the workflow is explicit.

#### House writing craft

This catalog's bar lives in `.agents/memory/system/skill-standards.md`. Apply it while editing SKILL.md:

- **Invocation.** Keep explicit entry points and advisory maps user-only with
  `disable-model-invocation: true`. Reusable engines omit it so a selected
  workflow can reach them. Loading an engine grants no action authority: forward
  the requested scope, existing authorization, and report-only restrictions.
  Put mutation gates in the body and require approval only for missing or expanded
  authority. Use direct execution routes for callable engines and recommendations
  for explicit-only workflows. Resolve resources from the selected installed
  skill directory, not an assumed repository checkout.
- **Leading words.** Collapse restated ideas into one pretrained token (`frontier`, `seam`, `tight`, `red`). Repeat the token; do not re-explain the sentence.
- **Completion criteria.** Every step ends on a checkable bound. Sharpen "understanding reached" into an observable ("frontier empty", "the narrow test fails for the missing behavior").
- **Prune no-ops.** Delete any sentence that does not change default model behavior.
- **Prompt the positive.** State the target behavior. Pair a hard prohibition with the positive target.
- **Contract.** Action, orchestrator, and side-effect skills include a `## Contract` block (inputs, outputs, creates/modifies, side effects, confirmation, delegates).
- **Provenance.** Skills derived from an upstream declare `source` / `upstream_repo` / `last_synced` and a README `## Upstream` section.

### Step 5: Packaging a Skill

Once the skill is ready, it should be packaged into a distributable zip file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:
   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a zip file named after the skill (e.g., `my-skill.zip`) that includes all files and maintains the proper directory structure for distribution.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

### Step 6: Iterate

After testing the skill, use observed failures or repeated friction to update
SKILL.md or bundled resources.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again
