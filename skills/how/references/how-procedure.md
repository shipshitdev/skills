## Distribution boundary

Use the active Shipshit skill catalog and the caller's existing authorization.
The harness owns host, account, model, effort, sandbox, worktree and schedule.
Upstream examples describe mechanisms; they do not grant permission or select
providers. Preserve report-only scope. External messages, publication, installs,
deployment and destructive actions require authorization covering that action.
Read configuration from the harness source of truth; never replace its role map
with an example here. Use only capabilities the active harness actually exposes.

# How

Explore the codebase to answer "how does X work?" questions. Produce clear architectural explanations at the level of a senior engineer onboarding onto a subsystem. Enough to build a working mental model, not annotated source code.

**Dispatch contract.** Resolve every configured role through `provider-dispatch.md` (resolve the `pstack` skill through the active catalog). Values are provider-qualified descriptors; the parent chooses native versus external execution. On Codex, resolve remaining Claude tool names via `codex-tools.md` (resolve the `pstack` skill through the active catalog).

This procedure only explains. For adversarial review of an architecture or a diff, route to `interrogate` or `structural-review`.

## Explain

### Step 1. Understand the Question and Assess Complexity

Parse what the user is asking about:

- "How does the rate limiter work?", a subsystem
- "How do we handle billing for on-demand usage?", a feature flow
- "How is the auth service structured?", an architectural overview
- "Walk me through what happens when a user submits a form", a runtime trace

Identify the scope. If ambiguous, state your best-guess interpretation before exploring. Don't ask. Let the user redirect if you're off.

**Assess complexity to decide the approach:**

- **Simple** (a single module, a small utility, a narrow question like "how does function X work"): skip explorer agents; the explainer explores and explains in a single pass. Go to Step 2b.
- **Complex** (a subsystem spanning multiple files/services, a cross-cutting feature, a full architectural overview): spawn parallel explorer agents first, then hand off to the explainer. Go to Step 2a.

When in doubt, lean simple. You can always spawn explorers if the explainer hits a wall.

### Step 2a. Explore (complex questions only)

Decompose the question into 2-4 parallel exploration angles, each a distinct slice of the subsystem so explorers don't duplicate work. Example split for "how does the rate limiter work?":

- Explorer 1: data model and state management
- Explorer 2: request path and enforcement
- Explorer 3: configuration and metrics infrastructure

The right decomposition depends on the question. Use your judgment. Narrow questions: 2 explorers is fine. Broad subsystems: up to 4.

Start all explorers in one fan-out phase through provider dispatch. Use your configured how-explorer descriptor from the active harness role map; use authorized parent-native exploration or report missing delegation coverage when this role is absent in `read-only` mode. A native lane uses the parent subagent primitive; an external lane uses the launcher directly.

Each explorer gets the same base prompt from `references/explorer-prompt.md` plus a specific exploration angle naming its slice. Each explorer should:

- Start broad: Glob for relevant directories, Grep for key types/interfaces/class names
- Follow the thread: from an entry point, trace the call chain (callers, callees, data flow, type definitions)
- Read the actual code, don't guess from file names
- Stop when it can describe the full path from input to output (or trigger to effect) without hand-waving any step
- Note things that are surprising, non-obvious, or that a newcomer would get wrong

Each explorer returns structured findings: components found, flow traced, files read, anything non-obvious. Overlap between explorers is fine; the explainer reconciles.

Then proceed to Step 3.

### Step 2b. Direct Explain (simple questions)

Dispatch one read-only lane that explores and explains in one pass using your configured how-explainer descriptor (from the active harness role map).

The agent does its own exploration (Glob, Grep, Read) and writes the explanation directly. Read `references/explainer-prompt.md` for the communication style and output format. Same structure, just no explorer findings as input.

Proceed to Step 4.

### Step 3. Synthesize (complex questions only)

Once all explorers return, dispatch one read-only lane to synthesize their findings into one coherent explanation using your configured how-explainer descriptor (from the active harness role map).

The explainer gets all explorers' findings and writes the human-facing explanation (output format below). Read `references/explainer-prompt.md` for the full prompt template. The explainer reconciles overlapping findings, resolves contradictions, and weaves the slices into a unified picture.

### Step 4. Present

Present the explainer's output to the user. You may lightly edit for clarity or add context from the conversation, but don't substantially rewrite. The explainer's communication is the product.

### Output Format

Follow this structure, adapted to the question. Not every section is needed for every question.

**Overview.** 1-2 paragraphs. What it is, what it does, why it exists. Enough to decide whether to keep reading.

**Key Concepts.** The important types, services, or abstractions. Brief definition of each. Not exhaustive, just the ones needed to understand the rest.

**How It Works.** The core of the explanation. Walk through the flow: what triggers it, what happens step by step, where data goes, the decision points. Prose, not pseudocode. Reference specific files and functions so the reader can go look, but don't dump code blocks unless a snippet is genuinely necessary.

**Where Things Live.** A brief map of the relevant files/directories. Not every file, just the ones needed to start working in this area.

**Gotchas.** Non-obvious or surprising things that would trip someone up. Historical context that explains why something looks weird. Known sharp edges.
