#!/bin/bash
#
# Cleanup Global Skill Duplicates
#
# Removes real directories from ~/.claude/skills/ that are duplicates
# of skills in this library. Leaves symlinks (community skills) untouched.
#
# Usage:
#   ./scripts/cleanup-global-duplicates.sh              # Dry run (default)
#   ./scripts/cleanup-global-duplicates.sh --execute     # Actually delete
#   ./scripts/cleanup-global-duplicates.sh --dry-run     # Explicit dry run
#
# What this does:
#   - Scans ~/.claude/skills/ for real directories (not symlinks)
#   - Matches them against skills/ in this repo
#   - Removes only the matches (library duplicates that were manually copied)
#   - Never touches symlinks (community skills managed by `npx skills`)
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LIBRARY_SKILLS_DIR="$REPO_ROOT/skills"
GLOBAL_SKILLS_DIR="$HOME/.claude/skills"

# Parse arguments
DRY_RUN=true
if [[ "${1:-}" == "--execute" ]]; then
  DRY_RUN=false
elif [[ "${1:-}" == "--dry-run" ]] || [[ -z "${1:-}" ]]; then
  DRY_RUN=true
else
  echo -e "${RED}Unknown option: $1${NC}"
  echo "Usage: $0 [--dry-run|--execute]"
  exit 1
fi

# Verify directories exist
if [[ ! -d "$LIBRARY_SKILLS_DIR" ]]; then
  echo -e "${RED}Library skills directory not found: $LIBRARY_SKILLS_DIR${NC}"
  exit 1
fi

if [[ ! -d "$GLOBAL_SKILLS_DIR" ]]; then
  echo -e "${YELLOW}Global skills directory not found: $GLOBAL_SKILLS_DIR${NC}"
  echo "Nothing to clean up."
  exit 0
fi

echo -e "${BLUE}=== Global Skills Cleanup ===${NC}"
echo ""
if $DRY_RUN; then
  echo -e "${YELLOW}DRY RUN — no files will be deleted${NC}"
  echo -e "${YELLOW}Run with --execute to actually delete${NC}"
else
  echo -e "${RED}EXECUTE MODE — duplicates will be deleted${NC}"
fi
echo ""

# Collect library skill names
library_skills=()
for dir in "$LIBRARY_SKILLS_DIR"/*/; do
  library_skills+=("$(basename "$dir")")
done

echo -e "Library skills found: ${GREEN}${#library_skills[@]}${NC}"

# Scan global skills for real directories matching library
duplicates=()
non_library_real_dirs=()
symlink_count=0

for entry in "$GLOBAL_SKILLS_DIR"/*/; do
  entry="${entry%/}"
  name="$(basename "$entry")"

  if [[ -L "$entry" ]]; then
    symlink_count=$((symlink_count + 1))
    continue
  fi

  # Real directory — check if it matches a library skill
  matched=false
  for lib_skill in "${library_skills[@]}"; do
    if [[ "$name" == "$lib_skill" ]]; then
      matched=true
      break
    fi
  done

  if $matched; then
    duplicates+=("$name")
  else
    non_library_real_dirs+=("$name")
  fi
done

echo -e "Symlinks (community, untouched): ${GREEN}${symlink_count}${NC}"
echo -e "Library duplicates to remove: ${RED}${#duplicates[@]}${NC}"

if [[ ${#non_library_real_dirs[@]} -gt 0 ]]; then
  echo -e "Non-library real dirs (untouched): ${YELLOW}${#non_library_real_dirs[@]}${NC}"
  for d in "${non_library_real_dirs[@]}"; do
    echo -e "  ${YELLOW}?${NC} $d"
  done
fi

echo ""

if [[ ${#duplicates[@]} -eq 0 ]]; then
  echo -e "${GREEN}No library duplicates found. Already clean.${NC}"
  exit 0
fi

# Process duplicates
echo -e "${BLUE}Library duplicates:${NC}"
removed=0
for name in "${duplicates[@]}"; do
  target="$GLOBAL_SKILLS_DIR/$name"
  if $DRY_RUN; then
    echo -e "  ${YELLOW}would remove${NC} $target"
  else
    rm -rf "$target"
    echo -e "  ${RED}removed${NC} $target"
    removed=$((removed + 1))
  fi
done

echo ""
if $DRY_RUN; then
  echo -e "${YELLOW}Dry run complete. ${#duplicates[@]} directories would be removed.${NC}"
  echo -e "Run with ${BLUE}--execute${NC} to delete."
else
  echo -e "${GREEN}Done. Removed $removed library duplicate directories.${NC}"
  echo ""
  echo -e "Next steps:"
  echo -e "  ${BLUE}npx skills add shipshitdev/skills --all${NC}  # Reinstall as managed symlinks"
fi
