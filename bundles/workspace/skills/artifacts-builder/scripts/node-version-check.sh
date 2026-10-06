#!/bin/bash
# Node.js version gate shared by the artifacts-builder scripts.
# Vite (npm view vite engines) requires: ^20.19.0 || >=22.12.0

# shellcheck disable=SC2034  # used by the scripts that source this file
NODE_MIN_DISPLAY="20.19.0+ or 22.12.0+"

# node_version_supported <version>
# Accepts exactly "v22.12.0" or "22.12.0" (what `node -v` prints for a release). Returns 0 when
# the full major.minor.patch satisfies the range above, 1 otherwise. Prereleases (22.12.0-rc.1),
# build metadata and any other suffix or malformed input are rejected, because a prerelease of
# a floor version does not satisfy the semver range.
# The ^20.19.0 and >=22.12.0 floors have patch 0, so any patch of the floor minor passes.
node_version_supported() {
  local re='^v?([0-9]+)\.([0-9]+)\.([0-9]+)$'
  [[ "$1" =~ $re ]] || return 1
  local major="${BASH_REMATCH[1]}" minor="${BASH_REMATCH[2]}"

  if [ "$major" -eq 20 ]; then
    [ "$minor" -ge 19 ]
  elif [ "$major" -eq 22 ]; then
    [ "$minor" -ge 12 ]
  else
    [ "$major" -gt 22 ]
  fi
}
