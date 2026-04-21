# Scaffold: Unified Project Scaffolder

Scaffold new projects or add components to existing projects with interactive prompts.

## Purpose

This command provides a unified way to scaffold:

- `.agents/` folder structure for AI-first development
- Backend (NestJS) with MongoDB, Swagger, and best practices
- Frontend (NextJS) with Tailwind, @agenticindiedev/ui, and TypeScript
- Mobile (Expo) with React Native and Expo Router
- Browser Extension (Plasmo) with React and Tailwind

## When to Use

Use this command when:

- Starting a new project from scratch
- Adding components to an existing project
- Setting up a monorepo or separate repositories
- Need to scaffold individual components (backend, frontend, mobile, extension)

## Usage

### Basic Usage

```bash
/scaffold
```

The AI will run the scaffold script interactively, asking you:

1. Project name
2. Project root path
3. Repository structure (monorepo vs separate)
4. Components to scaffold (all optional):
   - .agent folder
   - Backend (NestJS)
   - Frontend (NextJS)
   - Mobile (Expo)
   - Extension (Plasmo)
5. Organization name (for monorepo packages)

## Instructions for AI

When user invokes `/scaffold`:

### Step 1: Locate Script

Find the scaffold script:

```bash
# Check for Cursor skill:
~/.cursor/skills/project-init-orchestrator/scripts/scaffold.py
```

If not found, inform user they need to install the skill first.

### Step 2: Run Script

Execute the script in interactive mode:

```bash
python3 [script-path]
```

The script will handle all interactive prompts automatically.

### Step 3: Handle Output

- Display any errors or warnings from the script
- Show the generated structure
- Provide next steps (install dependencies, start development)

### Step 4: Verify Installation

If components were scaffolded, verify:

- Files were created successfully
- Directory structure is correct
- Entry files (AGENTS.md, CLAUDE.md, CODEX.md) exist

## Example Workflow

**User:** `/scaffold`

**AI Actions:**

1. Check if script exists: `ls -la ~/.cursor/skills/project-init-orchestrator/scripts/scaffold.py`
2. If found, run: `python3 ~/.cursor/skills/project-init-orchestrator/scripts/scaffold.py`
3. The script will ask interactive questions
4. Display results and next steps

**User:** "I want to add a backend to my existing project"

**AI Actions:**

1. Run scaffold script
2. When prompted, user selects:
   - Existing project path
   - Backend component only
   - Monorepo or separate structure
3. Script scaffolds backend into project
4. AI confirms completion

## Generated Structure

### Monorepo Example

```
myproject/
├── .agents/
├── package.json
├── api/              # NestJS backend
├── frontend/          # NextJS apps
├── mobile/            # Expo app
└── extension/         # Plasmo extension
```

### Separate Repos Example

```
myproject-api/        # Backend only
├── .agents/
└── apps/api/src/

myproject-frontend/   # Frontend only
├── .agents/
└── apps/dashboard/
```

## Integration

This command uses the `project-init-orchestrator` skill which:

- Integrates with `agent-folder-init` for .agent folder scaffolding
- Reuses templates from `fullstack-workspace-init`
- Works across Claude, Codex, and Cursor platforms

## Troubleshooting

**Script not found:**

- Install the skill: `ln -s /path/to/skills/.cursor/skills/project-init-orchestrator ~/.cursor/skills/project-init-orchestrator`
- Make script executable: `chmod +x ~/.cursor/skills/project-init-orchestrator/scripts/scaffold.py`

**Python not found:**

- Ensure Python 3 is installed: `python3 --version`
- Use `python3` instead of `python` if needed

**Permission denied:**

- Make script executable: `chmod +x ~/.cursor/skills/project-init-orchestrator/scripts/scaffold.py`

**Agent folder not created:**

- The script tries to use `agent-folder-init` skill
- If not found, it will skip .agent folder creation
- Install agent-folder-init skill for full support

## Next Steps After Scaffolding

1. **Install dependencies:**

   ```bash
   cd [project-root]
   bun install
   ```

2. **Start development:**

   ```bash
   # Monorepo
   bun run dev:api
   bun run dev:frontend

   # Separate repos
   cd api && bun run start:dev
   cd frontend && bun run dev
   ```

3. **Customize:**
   - Update `.agents/SYSTEM/RULES.md` with coding standards
   - Configure environment variables
   - Add your first features
