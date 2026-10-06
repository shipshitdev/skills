#!/bin/bash
# Node.js version gate shared by the artifacts-builder scripts.
# Vite (npm view vite engines) requires: ^20.19.0 || >=22.12.0

# shellcheck disable=SC2034  # used by the scripts that source this file
NODE_MIN_DISPLAY="20.19.0+ or 22.12.0+"

# node_version_supported <version>
# Accepts "v22.12.0", "22.12.0" or "22.12.0-nightly"; returns 0 when the full
# major.minor.patch satisfies the range above, 1 otherwise (including unparsable input).
# The ^20.19.0 and >=22.12.0 floors have patch 0, so any patch of the floor minor passes.
node_version_supported() {
  local raw="${1#v}"
  raw="${raw%%[-+]*}"
  local major minor patch
  IFS=. read -r major minor patch <<< "$raw"
  [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ && "$patch" =~ ^[0-9]+$ ]] || return 1

  if [ "$major" -eq 20 ]; then
    [ "$minor" -ge 19 ]
  elif [ "$major" -eq 22 ]; then
    [ "$minor" -ge 12 ]
  else
    [ "$major" -gt 22 ]
  fi
}
