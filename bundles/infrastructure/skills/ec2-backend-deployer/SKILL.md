---
name: ec2-backend-deployer
description: Deploys backend applications to EC2 instances using Docker, GitHub Actions CI/CD, and Tailscale for secure SSH access. Activates when setting up EC2 deployment pipelines, configuring container registries, or wiring automated deploys for NestJS, Next.js, or Express backends.
metadata:
  version: "2.2.2"
  tags: "ec2, deployment, backend"
---

# EC2 Backend Deployer

## Authorized Scope

Apply this engine only within the user's requested task and existing explicit
authorization. Loading or delegating to it grants no additional authority.
Preserve report-only restrictions and the caller's target, host, provider, and
cost limits. Existing approval satisfies a gate only for the same actions and
scope; obtain approval before expanding them. Forward these limits to delegates.

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

- `deploy` for the repository's release and deployment gates

## When to Use

Use when you're:

- Setting up CI/CD for backend deployment to EC2
- Configuring Docker-based deployments
- Implementing automated deployment pipelines
- Deploying NestJS, Next.js, or Express backends
- Setting up container registries and image management
- Configuring secure EC2 access (Tailscale)

## Quick Workflow

1. **Dockerfile**: Multi-stage build (base → builder → production)
2. **Registry**: GitHub Container Registry (ghcr.io) recommended
3. **CI/CD**: GitHub Actions with Tailscale for secure SSH
4. **Deploy**: Docker Compose on EC2 with health checks
5. **Verify**: Health endpoint + deployment verification

## Key Components

### Docker

- Multi-stage builds for smaller images
- Non-root user for security
- HEALTHCHECK for container orchestration
- BuildKit secrets for sensitive data

### GitHub Actions

- `docker/build-push-action` for image building
- `tailscale/github-action` for secure access
- `appleboy/ssh-action` for deployment

### EC2

- Docker Compose v2 required
- Health check verification
- Rollback procedures

## References

- [Full guide: Dockerfile, CI/CD workflow, deployment, troubleshooting](references/full-guide.md)
