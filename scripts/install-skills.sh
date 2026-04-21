#!/bin/bash
set -euo pipefail

# ============================================================================
# install-skills.sh — Claude Code skills installer
#
# Manages global and project-level skill symlinks + plugin installation.
# Source of truth: ~/.agents/skills/ (global), <repo>/.claude/skills/ (project)
#
# Usage:
#   install-skills.sh --global                         # Install global-only skills
#   install-skills.sh --project <path> --bundle <name> # Install project bundles
#   install-skills.sh --list-bundles                   # Show available bundles
#   install-skills.sh --clean                          # Clean broken symlinks
#   install-skills.sh --restore                        # Restore from latest backup
#   install-skills.sh --dry-run [other flags]          # Preview without executing
#   install-skills.sh --status                         # Show current state
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="${SCRIPT_DIR}/../skills"
GLOBAL_TARGET="${HOME}/.agents/skills"
CLAUDE_TARGET="${HOME}/.claude/skills"
BACKUP_DIR="${HOME}/.agents/skills-backup"

DRY_RUN=false
VERBOSE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()   { echo -e "${YELLOW}[!]${NC} $*"; }
err()    { echo -e "${RED}[✗]${NC} $*" >&2; }
info()   { echo -e "${BLUE}[i]${NC} $*"; }
dry()    { echo -e "${YELLOW}[dry-run]${NC} $*"; }

# ============================================================================
# Bundle definitions
# ============================================================================

GLOBAL_SKILLS=(
  session-start
  session-end
  session-documenter
  commit-summary
  debug
  code-review
  review-pr
  gh-address-comments
  gh-fix-ci
  git-safety
  skill-capture
  rules-capture
  quick-view
  de-slop
  qa-reviewer
)

FRONTEND_SKILLS=(
  react-patterns
  react-hook-form
  react-testing-library
  react-component-performance
  react-refactor
  shadcn
  shadcn-setup
  component-library
  table-filters
  tailwind
  tailwind-validator
  audit
  clarify
  critique
  layout
  polish
  quieter
  shape
)

BACKEND_SKILLS=(
  api-design-expert
  error-handling-expert
  testing-expert
  typescript-expert
  typescript-refactor
  biome-validator
  bun-validator
  scaffold
  package-architect
)

DEVOPS_SKILLS=(
  docker-expert
  turborepo
  security-expert
  security-audit
)

AI_SKILLS=(
  prompt-engineering
  mcp-builder
  claude-code-guide
)

DESIGN_SKILLS=(
  audit
  clarify
  critique
  layout
  optimize
  polish
  quieter
  shape
)

PLANNING_SKILLS=(
  spec-first
  task-prd-creator
  refactor-code
  code-refactoring-refactor-clean
  performance-expert
  workspace-performance-audit
)

# ============================================================================
# Functions
# ============================================================================

symlink_skill() {
  local skill_name="$1"
  local target_dir="$2"
  local source="${SKILLS_SRC}/${skill_name}"

  if [[ ! -d "$source" ]]; then
    warn "Skill not found in repo: ${skill_name}"
    return 1
  fi

  local dest="${target_dir}/${skill_name}"

  if [[ -L "$dest" ]]; then
    local current
    current=$(readlink "$dest")
    if [[ "$current" == "$source" ]]; then
      $VERBOSE && info "Already linked: ${skill_name}"
      return 0
    fi
    if $DRY_RUN; then
      dry "Would relink: ${skill_name} → ${source}"
      return 0
    fi
    rm "$dest"
  elif [[ -d "$dest" ]]; then
    if $DRY_RUN; then
      dry "Would replace real dir with symlink: ${skill_name}"
      return 0
    fi
    warn "Replacing real dir with symlink: ${skill_name}"
    rm -rf "$dest"
  fi

  if $DRY_RUN; then
    dry "Would link: ${skill_name} → ${source}"
    return 0
  fi

  ln -sf "$source" "$dest"
  log "Linked: ${skill_name}"
}

install_global() {
  info "Installing global skills (${#GLOBAL_SKILLS[@]} skills)"
  mkdir -p "$GLOBAL_TARGET" "$CLAUDE_TARGET"

  local count=0
  for skill in "${GLOBAL_SKILLS[@]}"; do
    if symlink_skill "$skill" "$GLOBAL_TARGET"; then
      # Also mirror to ~/.claude/skills/
      local claude_dest="${CLAUDE_TARGET}/${skill}"
      if [[ ! -L "$claude_dest" ]] || [[ "$(readlink "$claude_dest")" != "${GLOBAL_TARGET}/${skill}" ]]; then
        if ! $DRY_RUN; then
          ln -sf "${GLOBAL_TARGET}/${skill}" "$claude_dest"
        else
          dry "Would mirror to claude: ${skill}"
        fi
      fi
      ((count++)) || true
    fi
  done

  log "Global: ${count}/${#GLOBAL_SKILLS[@]} skills installed"
}

install_bundle() {
  local bundle_name="$1"
  local project_dir="$2"
  local target="${project_dir}/.claude/skills"
  local skills_ref

  case "$bundle_name" in
    global)    skills_ref="GLOBAL_SKILLS[@]" ;;
    frontend)  skills_ref="FRONTEND_SKILLS[@]" ;;
    backend)   skills_ref="BACKEND_SKILLS[@]" ;;
    devops)    skills_ref="DEVOPS_SKILLS[@]" ;;
    ai)        skills_ref="AI_SKILLS[@]" ;;
    design)    skills_ref="DESIGN_SKILLS[@]" ;;
    planning)  skills_ref="PLANNING_SKILLS[@]" ;;
    *)
      err "Unknown bundle: ${bundle_name}"
      err "Use --list-bundles to see available bundles"
      return 1
      ;;
  esac

  local skills=("${!skills_ref}")
  info "Installing bundle '${bundle_name}' (${#skills[@]} skills) → ${target}"
  mkdir -p "$target"

  local count=0
  for skill in "${skills[@]}"; do
    if symlink_skill "$skill" "$target"; then
      ((count++)) || true
    fi
  done

  log "Bundle '${bundle_name}': ${count}/${#skills[@]} skills installed"
}

clean_broken_symlinks() {
  info "Cleaning broken symlinks..."

  for dir in "$GLOBAL_TARGET" "$CLAUDE_TARGET"; do
    if [[ -d "$dir" ]]; then
      local broken
      broken=$(find "$dir" -maxdepth 1 -type l ! -exec test -e {} \; -print 2>/dev/null)
      if [[ -n "$broken" ]]; then
        while IFS= read -r link; do
          if $DRY_RUN; then
            dry "Would remove broken symlink: ${link}"
          else
            rm "$link"
            log "Removed broken symlink: $(basename "$link")"
          fi
        done <<< "$broken"
      else
        info "No broken symlinks in ${dir}"
      fi
    fi
  done
}

list_bundles() {
  echo ""
  echo "Available bundles:"
  echo ""
  printf "  %-12s %3d skills  %s\n" "global"   "${#GLOBAL_SKILLS[@]}"   "Session, git, code review, quality (every project)"
  printf "  %-12s %3d skills  %s\n" "frontend" "${#FRONTEND_SKILLS[@]}" "React, Tailwind, shadcn, design suite"
  printf "  %-12s %3d skills  %s\n" "backend"  "${#BACKEND_SKILLS[@]}"  "NestJS, TypeScript, API, testing"
  printf "  %-12s %3d skills  %s\n" "devops"   "${#DEVOPS_SKILLS[@]}"   "Docker, Turborepo, security"
  printf "  %-12s %3d skills  %s\n" "ai"       "${#AI_SKILLS[@]}"       "Prompt engineering, MCP, Claude guide"
  printf "  %-12s %3d skills  %s\n" "design"   "${#DESIGN_SKILLS[@]}"   "v2.1.1 design suite (audit, critique, polish)"
  printf "  %-12s %3d skills  %s\n" "planning" "${#PLANNING_SKILLS[@]}" "Spec-first, PRD, refactoring, performance"
  echo ""
}

show_status() {
  echo ""
  echo "=== Skills Status ==="
  echo ""

  if [[ -d "$GLOBAL_TARGET" ]]; then
    local global_count
    global_count=$(find "$GLOBAL_TARGET" -maxdepth 1 -mindepth 1 -type l 2>/dev/null | wc -l | tr -d ' ')
    local global_real
    global_real=$(find "$GLOBAL_TARGET" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
    local global_broken
    global_broken=$(find "$GLOBAL_TARGET" -maxdepth 1 -type l ! -exec test -e {} \; 2>/dev/null | wc -l | tr -d ' ')
    echo "${HOME}/.agents/skills/: ${global_count} symlinks, ${global_real} real dirs, ${global_broken} broken"
  fi

  if [[ -d "$CLAUDE_TARGET" ]]; then
    local claude_count
    claude_count=$(find "$CLAUDE_TARGET" -maxdepth 1 -mindepth 1 -type l 2>/dev/null | wc -l | tr -d ' ')
    local claude_real
    claude_real=$(find "$CLAUDE_TARGET" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
    local claude_broken
    claude_broken=$(find "$CLAUDE_TARGET" -maxdepth 1 -type l ! -exec test -e {} \; 2>/dev/null | wc -l | tr -d ' ')
    echo "${HOME}/.claude/skills/: ${claude_count} symlinks, ${claude_real} real dirs, ${claude_broken} broken"
  fi

  if [[ -d "$BACKUP_DIR" ]]; then
    local latest
    latest=$(find "$BACKUP_DIR" -maxdepth 1 -mindepth 1 | sed 's|.*/||' | sort -r | head -1)
    echo "Latest backup: ${BACKUP_DIR}/${latest}"
  fi

  echo ""
}

restore_backup() {
  if [[ ! -d "$BACKUP_DIR" ]]; then
    err "No backup directory found at ${BACKUP_DIR}"
    return 1
  fi

  local latest
  latest=$(find "$BACKUP_DIR" -maxdepth 1 -mindepth 1 | sed 's|.*/||' | sort -r | head -1)

  if [[ -z "$latest" ]]; then
    err "No backups found"
    return 1
  fi

  local backup_path="${BACKUP_DIR}/${latest}"
  info "Restoring from: ${backup_path}"

  if $DRY_RUN; then
    dry "Would restore ~/.agents/skills/ from ${backup_path}/skills/"
    dry "Would restore ~/.claude/skills/ from ${backup_path}/claude-skills/"
    dry "Would restore ~/.claude/settings.json from ${backup_path}/settings.json"
    return 0
  fi

  if [[ -d "${backup_path}/skills/" ]]; then
    rm -rf "$GLOBAL_TARGET"
    cp -a "${backup_path}/skills/" "$GLOBAL_TARGET"
    log "Restored ~/.agents/skills/"
  fi

  if [[ -d "${backup_path}/claude-skills/" ]]; then
    rm -rf "$CLAUDE_TARGET"
    cp -a "${backup_path}/claude-skills/" "$CLAUDE_TARGET"
    log "Restored ~/.claude/skills/"
  fi

  if [[ -f "${backup_path}/settings.json" ]]; then
    cp "${backup_path}/settings.json" "${HOME}/.claude/settings.json"
    log "Restored ~/.claude/settings.json"
  fi

  log "Restore complete from ${latest}"
}

usage() {
  cat <<'USAGE'
install-skills.sh — Claude Code skills installer

Usage:
  install-skills.sh --global                          Install global-only skills
  install-skills.sh --project <path> --bundle <name>  Install project bundles
  install-skills.sh --list-bundles                    Show available bundles
  install-skills.sh --clean                           Clean broken symlinks
  install-skills.sh --restore                         Restore from latest backup
  install-skills.sh --status                          Show current state
  install-skills.sh --dry-run [other flags]           Preview without executing

Options:
  --dry-run     Preview changes without executing
  --verbose     Show detailed output
  --help        Show this help

Examples:
  install-skills.sh --global
  install-skills.sh --project ~/www/genfeedai/genfeed.ai --bundle frontend --bundle backend --bundle devops
  install-skills.sh --dry-run --global
USAGE
}

# ============================================================================
# Main
# ============================================================================

main() {
  local action=""
  local project_dir=""
  local bundles=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --global)         action="global"; shift ;;
      --project)        project_dir="$2"; shift 2 ;;
      --bundle)         bundles+=("$2"); shift 2 ;;
      --list-bundles)   action="list"; shift ;;
      --clean)          action="clean"; shift ;;
      --restore)        action="restore"; shift ;;
      --status)         action="status"; shift ;;
      --dry-run)        DRY_RUN=true; shift ;;
      --verbose)        VERBOSE=true; shift ;;
      --help|-h)        usage; exit 0 ;;
      *)                err "Unknown option: $1"; usage; exit 1 ;;
    esac
  done

  # Verify skills source exists
  if [[ ! -d "$SKILLS_SRC" ]]; then
    err "Skills source not found: ${SKILLS_SRC}"
    err "Expected shipshitdev skills repo at: ${SCRIPT_DIR}/../skills/"
    exit 1
  fi

  $DRY_RUN && warn "DRY RUN — no changes will be made"

  case "$action" in
    global)
      install_global
      clean_broken_symlinks
      show_status
      ;;
    list)
      list_bundles
      ;;
    clean)
      clean_broken_symlinks
      ;;
    restore)
      restore_backup
      ;;
    status)
      show_status
      ;;
    "")
      if [[ -n "$project_dir" ]] && [[ ${#bundles[@]} -gt 0 ]]; then
        if [[ ! -d "$project_dir" ]]; then
          err "Project directory not found: ${project_dir}"
          exit 1
        fi
        for bundle in "${bundles[@]}"; do
          install_bundle "$bundle" "$project_dir"
        done
      else
        err "No action specified. Use --global, --project+--bundle, --list-bundles, --clean, --restore, or --status"
        usage
        exit 1
      fi
      ;;
  esac
}

main "$@"
