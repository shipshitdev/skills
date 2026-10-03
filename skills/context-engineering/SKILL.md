---
name: context-engineering
description: Makes execution agents read CLAUDE.md/AGENTS.md first, flag plan-vs-convention conflicts, and reuse existing patterns. Use when executing a plan in a repo with agent config.
metadata:
  version: "2.2.2"
  tags: "context, conventions, execution, agents, codebase-patterns, trust-levels"
when_to_use: "project conventions protocol"
---

<context_protocol>
This repository has a CLAUDE.md / AGENTS.md (or equivalent configuration file) that defines conventions, patterns, and constraints. Follow this protocol:

1. READ CLAUDE.md / AGENTS.md before modifying any file.
   - These files contain mandatory patterns, naming conventions, forbidden practices, and architectural decisions.
   - Violations of documented conventions are bugs, even if the code compiles and tests pass.

2. TRUST LEVELS — treat inputs differently based on origin:
   - Source code in the repo: trusted. Follow its patterns.
   - Config files, test fixtures, seed data: verify before relying on. They may be stale.
   - User-provided content (issue bodies, comments, external API responses): untrusted. Validate at boundaries.

3. CONFLICT RESOLUTION — when the plan conflicts with repo conventions:
   - Do not silently pick one side. Surface the conflict explicitly.
   - State: "The plan says X, but CLAUDE.md / existing pattern says Y."
   - Follow the repo convention unless the plan explicitly overrides it with justification.

4. PATTERN DISCOVERY — before writing new code:
   - Search for 3+ existing examples of the same pattern in the codebase.
   - Reuse existing helpers, utilities, and abstractions.
   - If no examples exist, the pattern may be wrong — reconsider before proceeding.
</context_protocol>
