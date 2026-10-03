#!/bin/bash
# Compatibility entry point: skills share package.json's release version.
# Check every canonical SKILL.md/plugin.json pair; no individual version bumps.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bun "$REPO_ROOT/scripts/sync-skill-versions.js" --check
