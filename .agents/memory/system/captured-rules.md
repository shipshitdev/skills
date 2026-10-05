# Captured Rules

Pending rules captured from working sessions. Review before promoting to permanent
repo standards.

## 2026-05-18 12:13 CEST - Skills: v0 Project Scaffolder for Init Skills

**User said:**

> "https://github.com/shipshitdev/v0 also, in all init skills, I want to make sure they are using my v0 project."

**Rule extracted:**

- **Type**: ALWAYS
- **Action**: New-project and project-initialization skills should route Shipshit.dev product scaffolding through `shipshitdev/v0` / `npx @shipshitdev/v0` instead of maintaining independent full-project scaffolding logic.
- **Context**: Applies to init/scaffold/orchestrator skills such as `project-init-orchestrator`, `agent-folder-init`, `landing-page-vercel`, `micro-landing-builder`, and related setup skills when creating a new Shipshit.dev-style product repo.
- **Category**: skills, scaffolding, workflow

**Status**: PENDING_REVIEW
