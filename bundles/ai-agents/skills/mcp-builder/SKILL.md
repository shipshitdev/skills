---
name: mcp-builder
description: >-
  Creates MCP (Model Context Protocol) servers that enable LLMs to interact with
  external services through well-designed tools. Activates on: "build an MCP server", "create
  MCP tools", "integrate API via MCP", "write a FastMCP server", "add an MCP server to an agent", or any
  request to wrap an external API as LLM-callable tools in Python or Node/TypeScript.
disable-model-invocation: true
license: Complete terms in LICENSE.txt
metadata:
  version: "2.2.2"
  source: https://github.com/anthropics/skills/blob/main/skills/mcp-builder/SKILL.md
  upstream_repo: anthropics/skills
  upstream_ref: main
  upstream_commit: ef740771ac90
  last_synced: "2026-06-12"
  license: Apache-2.0
  tags: "mcp, tools, agents"
---
# MCP Server Development Guide

# Process

## Contract

Inputs:

- Requested integration, target repository, API documentation, and approved service scope

Outputs:

- MCP server implementation, tool contracts, and scoped verification evidence

Creates/Modifies:

- Source, tests, and evaluation fixtures required for the requested server

External Side Effects:

- Documentation reads; provider calls and paid evaluations only when authorized

Confirmation Required:

- Before credentialed service writes, paid evaluation runs, publishing, or configuring an agent outside the requested scope
- Loading the skill grants no additional authority. Existing explicit approval
  applies only to the same target and actions; preserve report-only restrictions.

Delegates To:

- None

## High-Level Workflow

Build an MCP server in four phases:

### Phase 1: Deep Research and Planning

#### 1.1 Understand Agent-Centric Design Principles

Before implementation, design tools around agent workflows:

**Build for Workflows, Not Just API Endpoints:**

- Do not mirror every API endpoint by default. Group endpoints into workflow
  tools when one user task requires multiple API calls.
- Consolidate related operations (e.g., `schedule_event` that both checks availability and creates event)
- List the top user workflows and map each tool to one workflow.

**Optimize for Limited Context:**

- Return only fields needed for the task by default.
- Return high-signal information, not exhaustive data dumps
- Provide "concise" vs "detailed" response format options
- Default to human-readable identifiers over technical codes (names over IDs)
- Add pagination, field selection, or truncation for large responses.

**Design Actionable Error Messages:**

- Error messages include the failed field or operation, the cause, and the next
  valid action.
- Suggest specific next steps: "Try using filter='active_only' to reduce results"
- Never return raw provider errors without a tool-level explanation.

**Follow Natural Task Subdivisions:**

- Tool names should reflect how humans think about tasks
- Group related tools with consistent prefixes for discoverability
- Design tools around natural workflows, not just API structure

**Use Evaluation-Driven Development:**

- Create realistic evaluation scenarios early
- Let agent feedback drive tool improvements
- Prototype quickly and iterate based on actual agent performance

#### 1.2 Study MCP Protocol Documentation

**Fetch the MCP protocol documentation:**

Fetch: `https://modelcontextprotocol.io/llms-full.txt`

This document contains the complete MCP specification. Note: the URL may change as the spec evolves — if the fetch fails, search for the current MCP docs URL.

#### 1.3 Study Framework Documentation

**Load and read the following reference files:**

- **MCP Best Practices**: [📋 View Best Practices](./references/mcp_best_practices.md) - Core guidelines for all MCP servers

**For Python implementations, also load:**

- **Python SDK Documentation**: Fetch `https://py.sdk.modelcontextprotocol.io/`
- [🐍 Python Implementation Guide](./references/python_mcp_server.md) - Python-specific best practices and examples

**For Node/TypeScript implementations, also load:**

- **TypeScript SDK Documentation**: Fetch `https://ts.sdk.modelcontextprotocol.io/`
- [⚡ TypeScript Implementation Guide](./references/node_mcp_server.md) - Node/TypeScript-specific best practices and examples

#### 1.4 Study API Documentation

To integrate a service, read the API documentation for the selected workflows.
Scope endpoint and parameter coverage to those workflows, but read the
cross-cutting concerns (auth, rate limits, error handling, data models) in full
— they apply across every tool you expose:

- Official API reference documentation
- Authentication and authorization requirements
- Rate limiting and pagination patterns
- Error responses and status codes
- Available endpoints and their parameters
- Data models and schemas

Search or fetch documentation only for gaps that block the selected workflow.

#### 1.5 Create an Implementation Plan

Create a plan with these sections:

**Tool Selection:**

- List the most valuable endpoints/operations to implement
- Prioritize tools that enable the most common and important use cases
- Consider which tools work together to enable complex workflows

**Shared Utilities and Helpers:**

- Identify common API request patterns
- Plan pagination helpers
- Design filtering and formatting utilities
- Plan error handling strategies

**Input/Output Design:**

- Define input validation models (Pydantic for Python, Zod for TypeScript)
- Design consistent response formats (e.g., JSON or Markdown), and configurable levels of detail (e.g., Detailed or Concise)
- Plan for large-scale usage (thousands of users/resources)
- Implement character limits and truncation strategies (e.g., 25,000 tokens)

**Error Handling Strategy:**

- Plan graceful failure modes
- Define each error shape with: error code, human-readable cause, retryability,
  and next valid action.
- Consider rate limiting and timeout scenarios
- Handle authentication and authorization errors

---

### Phase 2: Implementation

After the plan exists, implement the shared infrastructure before individual
tools.

#### 2.1 Set Up Project Structure

**For Python:**

- Create a single `.py` file or organize into modules if complex (see [🐍 Python Guide](./references/python_mcp_server.md))
- Use the MCP Python SDK for tool registration
- Define Pydantic models for input validation

**For Node/TypeScript:**

- Create the project structure from [⚡ TypeScript Guide](./references/node_mcp_server.md)
- Set up `package.json` and `tsconfig.json`
- Use MCP TypeScript SDK
- Define Zod schemas for input validation

#### 2.2 Implement Core Infrastructure First

**To begin implementation, create shared utilities before implementing tools:**

- API request helper functions
- Error handling utilities
- Response formatting functions (JSON and Markdown)
- Pagination helpers
- Authentication/token management

#### 2.3 Implement Tools Systematically

For each tool in the plan:

**Define Input Schema:**

- Use Pydantic (Python) or Zod (TypeScript) for validation
- Include constraints (min/max length, regex patterns, min/max values, ranges)
- Describe field purpose, accepted values, and defaults
- Include diverse examples in field descriptions

**Write Tool Docstrings/Descriptions:**

- One-line summary of what the tool does
- Purpose and functionality
- Explicit parameter types with examples
- Return type schema
- Usage examples (when to use, when not to use)
- Error handling documentation, which outlines how to proceed given specific errors

**Implement Tool Logic:**

- Use shared utilities to avoid code duplication
- Follow async/await patterns for all I/O
- Implement the planned error shapes
- Support multiple response formats (JSON and Markdown)
- Respect pagination parameters
- Check character limits and truncate appropriately

**Add Tool Annotations:**

- `readOnlyHint`: true (for read-only operations)
- `destructiveHint`: false (for non-destructive operations)
- `idempotentHint`: true (if repeated calls have same effect)
- `openWorldHint`: true (if interacting with external systems)

#### 2.4 Follow Language-Specific Best Practices

Load the matching guide before finishing implementation — [🐍 Python Implementation Guide](./references/python_mcp_server.md) or [⚡ TypeScript Implementation Guide](./references/node_mcp_server.md) — and follow its patterns: proper SDK tool registration (`@mcp.tool` / `server.registerTool`), strict input validation (Pydantic v2 `model_config` / Zod `.strict()`), full type coverage with no `any`, async/await for all I/O, module-level constants for shared values (e.g. `CHARACTER_LIMIT`, `API_BASE_URL`), and — for TypeScript — a working `bun run build`.

---

### Phase 3: Review and Refine

After initial implementation:

#### 3.1 Code Quality Review

Review the code for:

- **DRY Principle**: No duplicated code between tools
- **Composability**: Shared logic extracted into functions
- **Consistency**: Similar operations return similar formats
- **Error Handling**: All external calls have error handling
- **Type Safety**: Full type coverage (Python type hints, TypeScript types)
- **Documentation**: Every tool has summary, parameters, return shape, examples,
  and error behavior

#### 3.2 Test and Build

**Important:** MCP servers are long-running processes that wait for requests over stdio/stdin or sse/http. Running them directly in the main process (e.g., `python server.py` or `node dist/index.js`) hangs it indefinitely.

Safe ways to test: run the server in tmux to keep it out of the main process, use a timeout (`timeout 5s python server.py`), or let the evaluation harness (Phase 4) manage the server subprocess directly for stdio transport.

- **Python:** verify syntax with `python -m py_compile your_server.py` and review imports.
- **Node/TypeScript:** run `bun run build`, confirm it completes without errors, and verify `dist/index.js` is created.

#### 3.3 Use Quality Checklist

To verify implementation quality, load the appropriate checklist from the language-specific guide:

- Python: see "Quality Checklist" in [🐍 Python Guide](./references/python_mcp_server.md)
- Node/TypeScript: see "Quality Checklist" in [⚡ TypeScript Guide](./references/node_mcp_server.md)

---

### Phase 4: Create Evaluations

After implementing the MCP server, create evaluations that test whether agents
can answer realistic questions with the tools.

**Load [✅ Evaluation Guide](./references/evaluation.md) for complete evaluation guidelines.**

#### 4.1 Understand Evaluation Purpose

Evaluations test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

#### 4.2 Create 10 Evaluation Questions

Follow the process outlined in the evaluation guide:

1. **Tool Inspection**: List available tools and understand their capabilities
2. **Content Exploration**: Use READ-ONLY operations to explore available data
3. **Question Generation**: Create 10 complex, realistic questions
4. **Answer Verification**: Solve each question yourself to verify answers

#### 4.3 Evaluation Requirements

Each question must be:

- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer that can be verified by string comparison
- **Stable**: Answer won't change over time

#### 4.4 Output Format

Create an XML file with this structure:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

## Gotchas

- **Running the server directly hangs the process.** MCP servers block on stdio/stdin waiting for requests indefinitely. Never run `python server.py` or `node dist/index.js` in your main process. Use `tmux` to background the server, or use the evaluation harness which manages the server subprocess.
- **Live URL references can go stale.** The MCP protocol documentation URL (`modelcontextprotocol.io/llms-full.txt`) and the GitHub SDK README URLs may move between versions. If a fetch fails, search for the current URL rather than assuming the skill path is correct.
- **TypeScript builds must be re-run after every source change.** `dist/index.js` is the artifact the MCP runtime loads. Editing `.ts` files without running `bun run build` means the runtime is still running the old version.
- **Tool annotations are hints, not enforced contracts.** `readOnlyHint: true` does not prevent a tool from writing data — it only signals intent to the LLM. Enforce safety in the tool implementation itself.

---

# Reference Files

Load only the resources required by the implementation language and phase.

| File | Load during | Covers |
|---|---|---|
| `references/mcp_best_practices.md` | Phase 1.3 (load first) | naming conventions, response formats (JSON vs Markdown), pagination, character limits/truncation, security and error-handling standards |
| `references/python_mcp_server.md` | Phase 2 (Python) | server init, Pydantic models, `@mcp.tool` registration, working examples, quality checklist |
| `references/node_mcp_server.md` | Phase 2 (TypeScript) | project structure, Zod schemas, `server.registerTool`, working examples, quality checklist |
| `references/evaluation.md` | Phase 4 | question-creation and answer-verification guidelines, XML format, example Q&A, running evaluations |

Also fetch the live protocol/SDK docs as needed: MCP protocol spec (`https://modelcontextprotocol.io/llms-full.txt`), Python SDK (`https://py.sdk.modelcontextprotocol.io/`), TypeScript SDK (`https://ts.sdk.modelcontextprotocol.io/`).
