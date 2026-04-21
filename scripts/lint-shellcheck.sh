#!/bin/bash
#
# Wrapper script for shellcheck that handles optional installation
# Used by lint-staged for pre-commit hooks
#

set -euo pipefail

if [[ $# -eq 0 ]]; then
  exit 0
fi

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck "$@"
else
  echo "⚠ shellcheck not installed. Install with: brew install shellcheck (macOS) or apt-get install shellcheck (Linux)"
  exit 0  # Don't fail if shellcheck is not installed
fi
