---
name: ec2-backend-deployer
description: Deploys backends to EC2 via Docker, GitHub Actions CI/CD, and Tailscale SSH. Use when wiring automated deploys for NestJS, Next.js, or Express to EC2.
metadata:
  version: "2.2.4"
  tags: "ec2, deployment, backend"
when_to_use: "container registry"
---

# EC2 Backend Deployer

## Scope

Act only within the user's request and existing approval; loading this skill grants no new authority. Keep report-only requests report-only, honor the caller's target, provider and cost limits, ask before expanding scope, and forward these limits to delegates.

## Contract

Inputs:

- Target repository, deployment goal, and approved AWS account/environment
- Existing Docker, registry, CI, and host-access configuration

Outputs:

- Scoped deployment configuration or a reviewed deployment plan
- Health-check evidence when deployment is authorized

Creates/Modifies:

- Docker and CI configuration within the requested setup
- Remote deployment state only when the target and operation are authorized

External Side Effects:

- Registry, CI, SSH, and AWS calls required for the approved deployment

Confirmation Required:

- Before creating billable infrastructure, changing secrets, or deploying outside
  the explicitly approved target and action
- Before replacing existing deployment configuration beyond the requested change

Delegates To:

- `deploy-app` for the repository's release and deployment gates

## When to use

- CI/CD for backend deployment to EC2
- Docker-based deployments and automated pipelines for NestJS, Next.js or Express
- Container registries and image management
- Secure EC2 access via Tailscale

## Quick workflow

1. **Dockerfile:** multi-stage build (base, builder, production).
2. **Registry:** GitHub Container Registry (ghcr.io) recommended.
3. **CI/CD:** GitHub Actions with Tailscale for secure SSH.
4. **Deploy:** Docker Compose on EC2 with health checks.
5. **Verify:** health endpoint and deployment verification.

## Key components

- **Docker:** multi-stage builds for smaller images; non-root user; `HEALTHCHECK`; BuildKit secrets for sensitive data.
- **GitHub Actions:** `docker/build-push-action` for images, `tailscale/github-action` for secure access, `appleboy/ssh-action` for deployment.
- **EC2:** Docker Compose v2 required; health-check verification; rollback procedures.

## References

[Full guide: Dockerfile, CI/CD workflow, deployment, troubleshooting](references/full-guide.md). Its example Dockerfiles and action versions are illustrative; check the repo's package manager (Bun by default), current supported base-image tags and current action versions before copying.
