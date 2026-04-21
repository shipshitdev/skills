---
name: project-init-orchestrator
description: Orchestrates complete project initialization — scaffolding, agent folders, linting, test coverage, and component setup (NestJS, Next.js, Expo, Plasmo). Use when starting a new project or adding infrastructure to an existing one.
metadata:
  version: "1.0.0"
  tags: project-init, scaffolding, orchestration, setup, monorepo
---

# Project Init Orchestrator

## Overview

This skill orchestrates multiple initialization skills to set up a complete, production-ready project environment. Instead of manually invoking each skill, this orchestrator coordinates them in the correct sequence with proper dependencies.

## When to Use This Skill

This skill activates automatically when users:

- Start a new project from scratch
- Want full project setup with one command
- Need AI-first development infrastructure + code quality tools
- Say "initialize project", "set up new project", "bootstrap project"
- Want consistent setup across multiple projects

## Skills Orchestrated

| Order | Skill | Purpose | Required |
|-------|-------|---------|----------|
| 1 | `agent-folder-init` | AI documentation & standards | Yes |
| 2 | `linter-formatter-init` | ESLint + Prettier + pre-commit | Yes |
| 3 | `husky-test-coverage` | Test coverage enforcement | Optional |
| 4 | Component scaffolding | Backend/Frontend/Mobile/Extension | Optional |

## Orchestration Flow

```
┌─────────────────────────────────────────────────────────────┐
│              PROJECT INIT ORCHESTRATOR                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: GATHER CONTEXT                                    │
│  • Project name and path                                    │
│  • Tech stack (Next.js, NestJS, Expo, Plasmo)              │
│  • Package manager preference (bun, pnpm, npm)             │
│  • Test coverage threshold (default: 80%)                  │
│  • Additional scaffolding needs                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: AGENT FOLDER INIT                                 │
│  • Create .agents/ directory structure                       │
│  • Set up SESSIONS/, TASKS/, SYSTEM/ folders               │
│  • Generate coding standards and rules                      │
│  • Copy agent configs (.claude/, .codex/, .cursor/)        │
│  ──────────────────────────────────────────────────────────│
│  Invocation:                                                │
│  python3 scripts/scaffold.py                               │
│          (from agent-folder-init skill)                    │
│          --root /path/to/project                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: LINTER FORMATTER INIT                             │
│  • Detect project tech stack                                │
│  • Install ESLint + Prettier (or Biome)                    │
│  • Configure framework-specific rules                       │
│  • Set up lint-staged for pre-commit                       │
│  • Create .vscode/settings.json                            │
│  ──────────────────────────────────────────────────────────│
│  Invocation:                                                │
│  Use linter-formatter-init skill guidance                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: HUSKY TEST COVERAGE (if tests exist)             │
│  • Detect test runner (Jest, Vitest, Mocha)                │
│  • Configure coverage thresholds                            │
│  • Add pre-commit hook for test coverage                   │
│  ──────────────────────────────────────────────────────────│
│  Invocation:                                                │
│  Use husky-test-coverage skill guidance                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: COMPONENT SCAFFOLD (optional)                     │
│  • Scaffold additional components if requested:            │
│    - Backend (NestJS + MongoDB + Swagger + Dockerfile)     │
│    - Frontend (Next.js + Tailwind + App Router)            │
│    - Mobile (Expo + Expo Router + React Native)            │
│    - Extension (Plasmo + React + Tailwind)                 │
│  • Supports monorepo (workspaces) or separate repos       │
│  ──────────────────────────────────────────────────────────│
│  Invocation:                                                │
│  python3 scripts/scaffold.py                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6: VERIFICATION                                      │
│  • Verify all configurations created                        │
│  • Run lint check (should pass)                            │
│  • Confirm git hooks installed                             │
│  • Generate setup summary                                   │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Quick Start (Recommended)

When user says "initialize my project" or "set up new project":

```
1. Ask for project context:
   - Project path (default: current directory)
   - Tech stack (Next.js, NestJS, Node.js, etc.)
   - Package manager (bun, pnpm, npm)
   - Test coverage threshold (default: 80%)
   - Need additional scaffolding? (backend, frontend, mobile, extension)

2. Execute phases in order:
   Phase 2 → Phase 3 → Phase 4 → Phase 5 (if needed) → Phase 6
```

### Manual Orchestration

If you need to run phases individually:

**Phase 2: Agent Folder Init**

```bash
python3 scripts/scaffold.py --root /path/to/project  # from agent-folder-init skill
```

**Phase 3: Linter Formatter**
Follow the `linter-formatter-init` skill to:

- Install dependencies based on detected stack
- Configure ESLint rules
- Set up Prettier
- Configure lint-staged

**Phase 4: Test Coverage**
Follow the `husky-test-coverage` skill to:

- Detect test runner
- Configure coverage thresholds
- Add pre-commit hook

**Phase 5: Component Scaffold (optional)**

```bash
python3 scripts/scaffold.py
```

Supports scaffolding:

- **Backend (NestJS)**: MongoDB, Swagger, soft deletes (`isDeleted`), multi-tenancy (filter by `organization`), Dockerfile
- **Frontend (Next.js)**: Tailwind CSS, TypeScript strict, App Router, path aliases (`@components/`, `@services/`, `@hooks/`)
- **Mobile (Expo)**: Expo Router, TypeScript, platform-specific configs
- **Extension (Plasmo)**: React + TypeScript, Tailwind, manifest config, popup component

Structure options:

- **Monorepo**: All components in one repo with workspace config
- **Separate repos**: Each component in its own directory
- **Existing projects**: Add components incrementally

## Configuration Presets

### Minimal (AI docs + linting)

```
Phases: 2, 3
Output:
├── .agents/
├── .eslintrc.js
├── .prettierrc
├── .husky/pre-commit (lint-staged)
└── .vscode/settings.json
```

### Standard (+ test coverage)

```
Phases: 2, 3, 4
Output:
├── .agents/
├── .eslintrc.js
├── .prettierrc
├── .husky/pre-commit (lint-staged + tests)
├── jest.config.js (coverage thresholds)
└── .vscode/settings.json
```

### Full Stack (+ scaffolding)

```
Phases: 2, 3, 4, 5
Output:
├── .agents/
├── apps/
│   ├── web/          (Next.js)
│   ├── api/          (NestJS)
│   ├── mobile/       (Expo)
│   └── extension/    (Plasmo)
├── packages/
│   └── shared/
├── .eslintrc.js
├── .prettierrc
├── .husky/pre-commit
└── .vscode/settings.json
```

## Generated Structure

After full orchestration, your project will have:

```
project-root/
├── .agents/                          # AI-first documentation
│   ├── SESSIONS/                    # Daily session logs
│   ├── TASKS/                       # Task tracking
│   │   └── INBOX.md
│   ├── SYSTEM/                      # Architecture docs
│   │   ├── ARCHITECTURE.md
│   │   └── RULES.md
│   └── README.md
│
├── .claude/                         # Claude Code configs
│   ├── commands/
│   ├── rules/
│   └── skills/
│
├── .husky/                          # Git hooks
│   └── pre-commit                   # Runs lint-staged + tests
│
├── .vscode/                         # Editor settings
│   └── settings.json                # Format on save
│
├── .eslintrc.js                     # ESLint configuration
├── .prettierrc                      # Prettier configuration
├── .lintstagedrc                    # Lint-staged configuration
│
└── [app directories if scaffolded]
```

## Best Practices

### Sequencing

- Always run agent-folder-init FIRST (establishes standards)
- Run linter-formatter-init BEFORE husky-test-coverage (both use Husky)
- Run component scaffolding LAST (depends on base setup)

### Customization

- Each phase can be skipped if already configured
- Phases are idempotent (safe to re-run)
- Configuration can be customized after orchestration

### Verification Checklist

After orchestration, verify:

- [ ] `.agents/` folder exists with proper structure
- [ ] `npm run lint` or `bun lint` works
- [ ] `npm run format` or `bun format` works
- [ ] Git commit triggers pre-commit hooks
- [ ] Tests run on commit (if Phase 4 enabled)

## Example Interaction

**User:** "Set up my new project at ~/projects/my-saas"

**Orchestrator Response:**

```
I'll initialize your project with full AI-first infrastructure.

Let me gather some context:
1. Tech stack: [Next.js / NestJS / Node.js / Other]
2. Package manager: [bun / pnpm / npm]
3. Test coverage threshold: [80% default]
4. Need scaffolding? [backend / frontend / mobile / extension]

[After user responds]

Starting orchestration...

✓ Phase 2: Agent Folder Init
  - Created .agents/ with 13 files
  - Copied agent configs (.claude/, .codex/, .cursor/)

✓ Phase 3: Linter Formatter Init
  - Detected: Next.js + TypeScript
  - Installed: eslint, prettier, lint-staged
  - Created: .eslintrc.js, .prettierrc, .lintstagedrc

✓ Phase 4: Husky Test Coverage
  - Detected: Jest
  - Set threshold: 80%
  - Added pre-commit hook

✓ Phase 6: Verification
  - All configs created ✓
  - Lint check passed ✓
  - Git hooks installed ✓

Project initialized successfully!
```

## Troubleshooting

### Phase fails to complete

- Check if dependencies are installed (`node`, `python3`)
- Verify write permissions to project directory
- Check if conflicting configs exist

### Linting errors after setup

- Run `npm run lint:fix` to auto-fix
- Check `.eslintrc.js` matches your stack
- Verify TypeScript config if using TS

### Pre-commit hook not running

- Run `npx husky install` manually
- Check `.husky/pre-commit` exists and is executable
- Verify `prepare` script in package.json
