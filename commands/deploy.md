---
description: "Deploy an app or set up deploy infra: compose a workflow, EC2 CI/CD, monitoring, or a dev container."
argument-hint: "[app|compose|ec2|monitor|devcontainer]"
disable-model-invocation: true
---

# Deploy - Single Front Door for Deployment and Infra Provisioning

Drive the full deployment and infra lifecycle from one command — ship an app to
staging or production, compose a repo-aware deployment workflow, wire an EC2
CI/CD pipeline, configure production monitoring, or scaffold a dev container.

## Usage

```bash
/deploy                  # status: domain overview + usage
/deploy app              # deploy web app to staging or production
/deploy compose          # compose the smallest safe deploy workflow from repo signals
/deploy ec2              # wire Docker + GitHub Actions CI/CD pipeline to EC2
/deploy monitor          # set up Sentry error tracking and Google Analytics
/deploy devcontainer     # scaffold a VS Code Dev Container with Docker
```

`/deploy help` prints this Usage block and stops without running anything.

## Steps

- **`app`** — the `deploy-app` skill: run deployment workflows for React, Next.js, or
  NestJS applications to preview, staging, or production, including pre-deploy
  gates, verification, and rollback guidance.
- **`compose`** — the `deployment-composer` skill: inspect the repository's actual
  branching model, CI setup, and deploy provider, then compose the smallest safe
  deployment workflow, routing to focused sub-skills for quality gates, provider
  deployment, post-deploy verification, and rollback.
- **`ec2`** — the `ec2-backend-deployer` skill: set up a Docker-based CI/CD
  pipeline for NestJS, Next.js, or Express backends on EC2, using GitHub Actions
  and Tailscale for secure SSH access.
- **`monitor`** — the `monitoring-setup` skill: configure Sentry error tracking
  and Google Analytics for NestJS and Next.js applications.
- **`devcontainer`** — the `devcontainer-setup` skill: scaffold a complete VS Code
  Dev Container configuration with Docker, docker-compose, and optional Claude
  Code CLI support.

## Workflow

Use the `deploy-dispatch` skill. It parses the subcommand and delegates to the
right engine. Read-only until the delegated skill's own confirmation gate; it
never mutates anything directly.

1. **Parse the argument** into a mode (`status` / `app` / `compose` / `ec2` /
   `monitor` / `devcontainer`). Unknown argument → print Usage, don't guess.
2. **Route** to the delegated skill (or, for `status`, print a domain overview
   and the Usage block, then stop).
3. **Defer** all preconditions and confirmation to the delegated skill — this
   command does not relax them.
4. **Never auto-chain** subcommands — each action is its own invocation.
