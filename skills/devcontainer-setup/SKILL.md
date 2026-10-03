---
name: devcontainer-setup
description: Scaffolds a VS Code Dev Container with Docker, docker-compose, and optional Claude Code CLI. Use when setting up a devcontainer or containerized dev environment.
metadata:
  version: "2.2.2"
  tags: "devcontainer, docker, setup"
when_to_use: "configure dev container, docker development environment"
---

# Devcontainer Setup Skill

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- Project runtime, existing container configuration, and requested development setup
- Approved directory mounts and optional tooling

Outputs:

- Dev Container configuration and startup instructions

Creates/Modifies:

- `.devcontainer/` files within the authorized setup scope

External Side Effects:

- Image pulls, package installs, or container startup only when requested

Confirmation Required:

- Before overwriting existing configuration or mounting directories outside the
  selected project
- Before adding tooling or starting containers outside the approved setup

Delegates To:

- `docker-expert` for container configuration details

## Information Gathering

Before creating the devcontainer, gather the following information from the user:

### Required Information

1. **Project Name**: What is the project/container name? (e.g., `my-project`, `shipshitdev-api`)

2. **Base Image**: What runtime does this project use?
   - `oven/bun:1.3.5` - Bun projects (recommended for speed)
   - `node:20-slim` - Node.js projects
   - `node:20` - Node.js with more tools
   - Custom image path

3. **Package Manager**: Which package manager?
   - `bun` - Bun (default for Bun projects)
   - `npm` - npm
   - `pnpm` - pnpm
   - `yarn` - Yarn

4. **Ports**: What ports need to be forwarded? (comma-separated, e.g., `3000, 3001, 5432`)

5. **Port Labels** (optional): Labels for each port (e.g., `3000=Web, 5432=Postgres`)

6. **Parent Directory Mount**: Should the parent directory be mounted for cross-repo access?
   - Yes - Mount parent as `/workspace` (good for monorepos, shared libraries)
   - No - Only mount this project

7. **Claude Code Support**: Include Claude Code CLI setup?
   - Yes - Install Claude Code and fix symlinks for container use
   - No - Skip Claude Code setup

8. **VS Code Extensions** (optional): Additional extensions to install (comma-separated extension IDs)

9. **Monorepo Structure** (if applicable):
   - Is this a monorepo with nested package.json files?
   - What are the app/package directories? (e.g., `apps/*, packages/*`)

## File Structure to Create

```
.devcontainer/
├── devcontainer.json      # VS Code dev container config
├── Dockerfile             # Container image definition
├── docker-compose.yml     # Docker compose config
├── setup.sh               # Post-create setup script
└── README.md              # Documentation
```

## Templates

Generate all five files from the gathered information:

- `devcontainer.json` — build config, mounts, features, VS Code extensions/settings, forwarded ports, `postCreateCommand`
- `Dockerfile` — base image, workdir, dependency install (monorepo-aware), dev tools, exposed ports
- `docker-compose.yml` — service definition, volumes (parent mount + node_modules caching), ports, dev command
- `setup.sh` — installs dependencies; if Claude Code support is requested, also fixes host-to-container Claude config symlinks and prints API key setup instructions
- `README.md` — quick start, mount/port tables, directory structure, troubleshooting

See `references/templates.md` for the full fill-in-the-blank text of each file
(`{{PLACEHOLDER}}` values come from the gathered information above).

## Package Manager Reference

| Package Manager | Lock File | Install Command | Dev Command |
|-----------------|-----------|-----------------|-------------|
| bun | `bun.lock*` | `bun install --frozen-lockfile` | `bun run dev` |
| npm | `package-lock.json` | `npm ci` | `npm run dev` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | `pnpm run dev` |
| yarn | `yarn.lock` | `yarn install --frozen-lockfile` | `yarn dev` |

## Implementation Steps

1. Ask the user the required questions above using AskUserQuestion
2. Create the `.devcontainer` directory
3. Generate each file with the gathered configuration
4. Make `setup.sh` executable
5. Provide summary of what was created and how to use it

## Example Usage

User: "Set up devcontainer for my Next.js project"

1. Gather info: Project uses Bun, ports 3000, needs Claude Code support
2. Create all 5 files in `.devcontainer/`
3. Output: "Created devcontainer configuration. Open in VS Code and click 'Reopen in Container'."
