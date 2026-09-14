#!/bin/bash
set -euo pipefail

# ============================================================================
# setup-dev-loop.sh — provision the AI dev loop on a GitHub repo
#
# One-shot, idempotent setup for label-driven autonomous execution. Three engine
# lanes share one label contract: the Claude lane (dispatch:claude), the Codex/GPT
# lane (dispatch:codex), and the OpenRouter lane (dispatch:openrouter). Status is NOT
# a label — it is the GitHub
# Projects board `Status` field (Backlog / In Progress / Human Review / Done / Deferred), the sole
# source of truth, which this script provisions.
#   1. Migrates legacy label names in place, then creates the dispatch label
#      vocabulary (claim:active, priority:*, rejection:N, dispatch:plan,
#      dispatch:claude, dispatch:codex, dispatch:openrouter, type:feature,
#      wontfix). The two old status:* labels are deleted — status moves to the
#      board.
#   2. Provisions the Projects board: creates-or-reuses the project, normalizes
#      its Status options to Backlog/In Progress/Human Review/Done/Deferred, and writes the board's
#      node ids to .github/agent-loop.env (non-secret) for the workflows + /loop.
#   3. Installs the Phase-2 push workflows (.github/workflows/plan-dispatch.yml
#      for the planning gate, agent-dispatch.yml for Claude, codex-dispatch.yml
#      for Codex, openrouter-dispatch.yml for OpenRouter).
#   4. Arms the auth secrets — CLAUDE_CODE_OAUTH_TOKEN (subscription OAuth, never
#      an API key), OPENAI_API_KEY (Codex lane), and PROJECTS_TOKEN (a project-
#      scoped PAT the workflows use to write the board; the default GITHUB_TOKEN
#      cannot touch an org-owned Projects v2 board).
#   5. Prints explicit planner/executor model and effort variables; no fallback.
#   6. Points you at /setup-agent-routing for the per-repo routing block.
#
# Operates on the current repo by default (resolved via `gh`); override with
# --repo owner/name. Safe to re-run — labels use --force, the board normalize is
# idempotent, workflows are copied in place, secrets are left alone if already set.
#
# Usage:
#   setup-dev-loop.sh                       # set up the current repo
#   setup-dev-loop.sh --repo owner/name     # target a specific repo
#   setup-dev-loop.sh --project 7           # reuse an existing board number
#   setup-dev-loop.sh --dry-run             # preview without changing anything
#   setup-dev-loop.sh --skip-board          # skip board provisioning
#   setup-dev-loop.sh --skip-secrets        # skip the auth-secret steps
#   setup-dev-loop.sh --help
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="${SCRIPT_DIR}/../.github/workflows"
# Board normalizer (sets the Status options to the 5-column model).
BOARD_SCRIPT="${SCRIPT_DIR}/../skills/project-board/scripts/setup-github-board.mjs"

# Phase-2 push workflows installed into the target repo: one planning gate
# (plan-dispatch.yml, dispatch:plan) plus one execution lane per engine.
# Fixed companion set shipped from the same checkout as the workflows.
# Copy complete skill directories so relative scripts/references remain usable.
DISPATCH_SKILLS=(
  prd-writer prd-task-creator feature-intake writing-plans prd-quality-gate
  executing-plans tdd qa-reviewer github-pr-publish verification-before-completion
  commit-summary github-fix-ci testing-expert ai-regression-testing
)

WORKFLOWS=(
  "plan-dispatch.yml"
  "agent-dispatch.yml"
  "codex-dispatch.yml"
  "openrouter-dispatch.yml"
)

# The 5-column board model. The board Status field is the SOLE source of truth
# for where an issue sits — there are no status:* labels.
BOARD_STATUS="Backlog,In Progress,Human Review,Done,Deferred"
# Title used to create-or-reuse the project when --project is not given.
PROJECT_TITLE="Dev Loop"

REPO=""
REPO_FLAG=()
PROJECT_NUMBER=""
DO_LABELS=true
DO_WORKFLOW=true
DO_BOARD=true
DO_SECRETS=true
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
vlog() {
  if $VERBOSE; then
    echo -e "${BLUE}[v]${NC} $*"
  fi
}

# ============================================================================
# Dispatch label vocabulary — name|color|description.
# Mirrors skills/setup-agent-routing/references/triage-labels.md.
# Status is the board's Status field, not a label, so no status:* entries here.
# ============================================================================

LABELS=(
  "claim:active|5319e7|An agent holds this issue; stale claims require explicit recovery"
  "priority:high|b60205|Queue ordering — picked first"
  "priority:medium|d93f0b|Queue ordering — picked after high"
  "priority:low|0e8a16|Queue ordering — picked last"
  "rejection:1|e99695|QA rejection count — 1st kickback from Human Review"
  "rejection:2|e99695|QA rejection count — 2nd kickback from Human Review"
  "rejection:3|e99695|QA rejection count — 3rd kickback from Human Review"
  "dispatch:claude|006b75|Dispatch gate (human opt-in) — Claude lane runs only on issues carrying this"
  "dispatch:codex|10a37f|Dispatch gate (human opt-in) — Codex/GPT lane runs only on issues carrying this"
  "dispatch:openrouter|8250df|Dispatch gate (human opt-in) — OpenRouter lane (Codex CLI via OpenRouter) runs only on issues carrying this"
  "dispatch:plan|fbca04|Planning gate (human opt-in) — prepares a decision-complete issue and plan; applies no execution gate"
  "loop:planning|c5def5|AI-loop phase — preparing decisions and checking execution readiness"
  "loop:executing|c5def5|AI-loop phase — implementing the change on a branch (inside In Progress)"
  "loop:testing|c5def5|AI-loop phase — running qa-reviewer + automated tests/e2e (inside In Progress)"
  "loop:shipping|c5def5|AI-loop phase — opening the PR (inside In Progress)"
  "type:feature|a2eeef|Applied by feature-intake to PRD epics and their sub-issues"
  "wontfix|ffffff|Closed; will not be actioned"
)

# Legacy → new name migrations, applied IN PLACE before seeding so existing
# issues keep their label (gh label edit preserves assignments). old|new.
LABEL_RENAMES=(
  "ready-for-agent|dispatch:claude"
  "ready-for-codex|dispatch:codex"
  "claimed|claim:active"
  "feature|type:feature"
)

# Legacy labels retired entirely — status now lives on the board.
LABEL_DELETES=(
  "status:todo"
  "status:testing"
)

# ============================================================================
# Preflight
# ============================================================================

require_gh() {
  command -v gh >/dev/null 2>&1 || {
    err "gh CLI not found — install it: https://cli.github.com"
    exit 1
  }
  gh auth status >/dev/null 2>&1 || {
    err "gh is not authenticated — run: gh auth login"
    exit 1
  }
}

resolve_repo() {
  if [[ -z "$REPO" ]]; then
    REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || true)"
  fi
  if [[ -z "$REPO" ]]; then
    err "Could not detect a GitHub repo. Run inside a repo with a GitHub remote, or pass --repo owner/name"
    exit 1
  fi
  REPO_FLAG=(--repo "$REPO")
  vlog "repo resolved: ${REPO}"
}

# ============================================================================
# Step 1 — labels
# ============================================================================

# Rename legacy labels in place (preserves assignments on open issues) and delete
# the retired status:* labels. Runs BEFORE create_labels so the new names are not
# already taken when `gh label edit` tries to rename onto them. Idempotent: on a
# fresh repo the legacy labels are absent and every step is a harmless no-op.
migrate_labels() {
  info "Migrating legacy label names in place on ${REPO}"
  local entry old new name
  for entry in "${LABEL_RENAMES[@]}"; do
    IFS='|' read -r old new <<<"$entry"
    if $DRY_RUN; then
      dry "gh label edit '${old}' --name '${new}'  (migrates the label on all open issues)"
      continue
    fi
    if gh label edit "$old" --name "$new" "${REPO_FLAG[@]}" >/dev/null 2>&1; then
      log "renamed label: ${old} -> ${new}"
    else
      vlog "no legacy label '${old}' to rename (fresh repo or already migrated)"
    fi
  done
  for name in "${LABEL_DELETES[@]}"; do
    if $DRY_RUN; then
      dry "gh label delete '${name}' --yes  (status moves to the board)"
      continue
    fi
    if gh label delete "$name" --yes "${REPO_FLAG[@]}" >/dev/null 2>&1; then
      log "deleted retired status label: ${name}"
    else
      vlog "no legacy label '${name}' to delete"
    fi
  done
}

create_labels() {
  info "Creating/updating ${#LABELS[@]} dispatch labels on ${REPO}"
  local entry name color desc
  for entry in "${LABELS[@]}"; do
    IFS='|' read -r name color desc <<<"$entry"
    if $DRY_RUN; then
      dry "gh label create '${name}' --color ${color} --force"
      continue
    fi
    if gh label create "$name" --color "$color" --description "$desc" --force "${REPO_FLAG[@]}" >/dev/null 2>&1; then
      log "label: ${name}"
    else
      err "failed to create label: ${name}"
    fi
  done
}

# ============================================================================
# Step 2 — push workflow
# ============================================================================

install_workflows() {
  local repo_root
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -z "$repo_root" ]]; then
    warn "not inside a git working tree — skipping workflow copy"
    info "add these to .github/workflows/ in the target repo manually:"
    local wf
    for wf in "${WORKFLOWS[@]}"; do info "  ${WORKFLOW_DIR}/${wf}"; done
    return
  fi
  if ! $DRY_RUN; then mkdir -p "${repo_root}/.github/workflows"; fi
  local wf src dest
  for wf in "${WORKFLOWS[@]}"; do
    src="${WORKFLOW_DIR}/${wf}"
    dest="${repo_root}/.github/workflows/${wf}"
    if [[ ! -f "$src" ]]; then
      err "workflow source missing: ${src}"
      continue
    fi
    if [[ "$dest" -ef "$src" ]]; then
      info "${wf} already lives in this repo — nothing to copy"
      continue
    fi
    if $DRY_RUN; then
      dry "cp ${src} ${dest}"
      continue
    fi
    [[ -f "$dest" ]] && warn "${wf} exists — overwriting with the bundled version"
    cp "$src" "$dest"
    log "workflow installed: .github/workflows/${wf}"
  done
  local skill
  for skill in "${DISPATCH_SKILLS[@]}"; do
    src="${SCRIPT_DIR}/../skills/${skill}"
    dest="${repo_root}/.github/agent-skills/${skill}"
    [[ -f "${src}/SKILL.md" ]] || { err "required dispatch skill missing: ${src}"; return 1; }
    if $DRY_RUN; then
      dry "copy complete skill ${src} to ${dest}"
    else
      mkdir -p "$dest"
      cp -R "${src}/." "$dest/"
    fi
  done
  local resource
  for resource in agent-dispatch.cjs agent-dispatch.md; do
    src="${WORKFLOW_DIR}/../${resource}"
    dest="${repo_root}/.github/${resource}"
    [[ -f "$src" ]] || { err "required dispatch resource missing: ${src}"; return 1; }
    if [[ "$dest" -ef "$src" ]]; then continue; fi
    if $DRY_RUN; then dry "cp ${src} ${dest}"; else cp "$src" "$dest"; fi
  done
}

# ============================================================================
# Step 2.5 — provision the GitHub Projects board (status source of truth)
# ============================================================================

# Create-or-reuse the project, normalize its Status options to the 5-column model,
# and write the board's node ids to .github/agent-loop.env so the workflows + /loop
# can flip Status via `gh project item-edit`. Status is a board field, not a label.
# Needs the user's gh auth to carry the `project` scope (local runs do; CI uses the
# PROJECTS_TOKEN secret instead).
provision_board() {
  local owner repo_root num node_id fields_json status_field_id env_file
  local backlog_id in_progress_id human_review_id done_id deferred_id
  owner="${REPO%%/*}"
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -z "$repo_root" ]]; then
    err "Not inside the target repository working tree; cannot write .github/agent-loop.env"
    return 1
  fi
  env_file="${repo_root}/.github/agent-loop.env"

  if $DRY_RUN; then
    dry "resolve-or-create project '${PROJECT_TITLE}' under ${owner} (or reuse --project ${PROJECT_NUMBER:-<auto>})"
    dry "node ${BOARD_SCRIPT} --owner ${owner} --project <num> --status \"${BOARD_STATUS}\" --exact --apply"
    dry "write board node ids (PROJECT_NODE_ID, STATUS_FIELD_ID, STATUS_*_OPTION_ID) to ${env_file}"
    return
  fi

  command -v node >/dev/null 2>&1 || { err "node not found — needed to normalize the board"; return 1; }
  command -v jq   >/dev/null 2>&1 || { err "jq not found — needed to read board ids"; return 1; }
  [[ -f "$BOARD_SCRIPT" ]] || { err "board normalizer missing: ${BOARD_SCRIPT}"; return 1; }

  # 1. Resolve the project number: explicit --project wins; else reuse a project
  #    titled "$PROJECT_TITLE"; else create + link one.
  num="$PROJECT_NUMBER"
  if [[ -z "$num" ]]; then
    num="$(gh project list --owner "$owner" --format json 2>/dev/null \
      | jq -r --arg t "$PROJECT_TITLE" 'first(.projects[] | select(.title == $t) | .number) // empty')"
  fi
  if [[ -z "$num" ]]; then
    info "creating project '${PROJECT_TITLE}' under ${owner}"
    num="$(gh project create --owner "$owner" --title "$PROJECT_TITLE" --format json | jq -r '.number')"
    gh project link "$num" --owner "$owner" --repo "$REPO" >/dev/null 2>&1 || true
  else
    info "reusing project #${num} under ${owner}"
  fi

  # 2. Normalize the Status options to exactly Backlog/In Progress/Human Review/Done/Deferred. Pass
  #    --status explicitly to pin the column set regardless of the normalizer's
  #    default; --exact prunes any other option, --apply writes (default is dry-run).
  info "normalizing board #${num} Status options to: ${BOARD_STATUS}"
  node "$BOARD_SCRIPT" --owner "$owner" --project "$num" --status "$BOARD_STATUS" --exact --apply

  # 3. Read the live field + option ids and write the non-secret env file.
  node_id="$(gh project view "$num" --owner "$owner" --format json | jq -r '.id')"
  fields_json="$(gh project field-list "$num" --owner "$owner" --format json)"
  status_field_id="$(jq -r '.fields[] | select(.name == "Status") | .id' <<<"$fields_json")"
  _opt_id() { jq -r --arg n "$1" '.fields[] | select(.name == "Status") | .options[]? | select(.name == $n) | .id' <<<"$fields_json"; }
  backlog_id="$(_opt_id "Backlog")"
  in_progress_id="$(_opt_id "In Progress")"
  human_review_id="$(_opt_id "Human Review")"
  done_id="$(_opt_id "Done")"
  deferred_id="$(_opt_id "Deferred")"

  local missing_ids=()
  [[ -z "$node_id" ]] && missing_ids+=("PROJECT_NODE_ID")
  [[ -z "$status_field_id" ]] && missing_ids+=("STATUS_FIELD_ID")
  [[ -z "$backlog_id" ]] && missing_ids+=("STATUS_BACKLOG_OPTION_ID")
  [[ -z "$in_progress_id" ]] && missing_ids+=("STATUS_IN_PROGRESS_OPTION_ID")
  [[ -z "$human_review_id" ]] && missing_ids+=("STATUS_HUMAN_REVIEW_OPTION_ID")
  [[ -z "$done_id" ]] && missing_ids+=("STATUS_DONE_OPTION_ID")
  [[ -z "$deferred_id" ]] && missing_ids+=("STATUS_DEFERRED_OPTION_ID")
  if ((${#missing_ids[@]} > 0)); then
    err "Failed to resolve board IDs: ${missing_ids[*]}. Aborting env file write."
    return 1
  fi

  mkdir -p "$(dirname "$env_file")"
  cat >"$env_file" <<EOF
# Generated by setup-dev-loop.sh — committed, NON-SECRET board node ids.
# Workflows + /loop source this to flip the board Status field. Only PROJECTS_TOKEN
# is secret. Re-run setup-dev-loop.sh to regenerate after the board changes.
PROJECT_OWNER=${owner}
PROJECT_NUMBER=${num}
PROJECT_NODE_ID=${node_id}
STATUS_FIELD_ID=${status_field_id}
STATUS_BACKLOG_OPTION_ID=${backlog_id}
STATUS_IN_PROGRESS_OPTION_ID=${in_progress_id}
STATUS_HUMAN_REVIEW_OPTION_ID=${human_review_id}
STATUS_DONE_OPTION_ID=${done_id}
STATUS_DEFERRED_OPTION_ID=${deferred_id}
EOF
  log "board ids written: ${env_file}"
}

# ============================================================================
# Step 3 — auth secrets (Phase-2 auth, one per engine lane + board write)
# ============================================================================

# setup_one_secret <NAME> <hint>
# Idempotent: leaves an already-set secret alone; otherwise prompts (interactive
# only) to set it via `gh secret set`, which reads the value with input hidden.
setup_one_secret() {
  local name="$1" hint="$2" existing reply
  existing="$(gh secret list "${REPO_FLAG[@]}" --json name --jq '.[].name' 2>/dev/null | grep -Fx "$name" || true)"
  if [[ -n "$existing" ]]; then
    log "secret ${name} already set"
    return
  fi
  warn "secret ${name} is not set on ${REPO}"
  info "${hint}"
  if $DRY_RUN; then
    dry "gh secret set ${name} ${REPO_FLAG[*]}"
    return
  fi
  if [[ ! -t 0 ]]; then
    warn "non-interactive shell — set it later:  gh secret set ${name} ${REPO_FLAG[*]}"
    return
  fi
  printf '%b' "${BLUE}[i]${NC} Set ${name} now? gh will prompt for the value (input hidden). [y/N] "
  read -r reply
  if [[ "$reply" =~ ^[Yy]$ ]]; then
    gh secret set "$name" "${REPO_FLAG[@]}"
    log "secret ${name} set"
  else
    info "skipped — set it later:  gh secret set ${name}"
  fi
}

setup_secrets() {
  # Claude lane (dispatch:claude). Subscription OAuth only — never an API key.
  setup_one_secret "CLAUDE_CODE_OAUTH_TOKEN" \
    "Claude lane — generate with:  claude setup-token   (uses your Claude subscription, never an API key)"
  # Codex/GPT lane (dispatch:codex). Skip if you only run the Claude lane.
  setup_one_secret "OPENAI_API_KEY" \
    "Planner/Codex lanes — an OpenAI API key from https://platform.openai.com/api-keys (required for dispatch:plan and dispatch:codex)"
  # OpenRouter lane (dispatch:openrouter). Skip if you only run Claude/Codex.
  setup_one_secret "OPENROUTER_API_KEY" \
    "OpenRouter lane — an OpenRouter API key from https://openrouter.ai/keys (skip if you don't use the OpenRouter lane)"
  # Board write (all lanes). A project-scoped PAT — the default GITHUB_TOKEN
  # cannot read/write an org-owned Projects v2 board. YOU paste it at the hidden
  # gh prompt; it is never generated, echoed, or stored by this script.
  setup_one_secret "PROJECTS_TOKEN" \
    "Board write — a PAT with 'project' scope (classic: project + repo; or fine-grained: org Projects read/write + repo write). Create at https://github.com/settings/tokens"
}

# ============================================================================
# Step 4 — model selection (repo VARIABLES, not secrets)
# ============================================================================

# Role configuration is explicit and separate; setup never guesses capacity.
print_variables_step() {
  info "Required runtime variables for the lanes you use (no model fallback):"
  echo "      Planner: PLANNER_MODEL + PLANNER_EFFORT (OpenAI planning role)"
  echo "      Codex executor: CODEX_MODEL + CODEX_EFFORT"
  echo "      Claude executor: CLAUDE_MODEL + CLAUDE_EFFORT (replaces AGENT_MODEL)"
  echo "      OpenRouter executor: OPENROUTER_MODEL + OPENROUTER_EFFORT + OPENROUTER_PROVIDER"
  echo "      Set each with: gh variable set VARIABLE --body '<approved-value>' ${REPO_FLAG[*]}"
  echo "      OPENROUTER_PROVIDER names the actual model lab; automatic model routing is rejected."
  echo "      No usage telemetry or subscription-capacity routing is installed. Codex Actions use API credentials."
  echo "      Provision a separate frontier reviewer from a different provider for every implementation."
  echo "      These workflows stop at review-pending; they do not provision reviewer automation or branch protection."
  echo "      Setup copies the prepared workflow skill set and complete resources into .github/agent-skills/."
  echo "      Missing skills, runtime settings, or board configuration block dispatch."
}

print_routing_step() {
  info "Final step — write this repo's routing block so the loop skills know your tracker + labels:"
  echo "      In Claude Code, run:  /setup-agent-routing"
  echo "      (writes the '## Agent skills' block + docs/agents/*.md, with your confirmation)"
}

print_summary() {
  echo ""
  log "Dev-loop setup complete on ${REPO}"
  $DO_LABELS   && echo "  • Labels:    dispatch:plan / dispatch:claude / dispatch:codex / claim:active / loop:* (AI-loop phases) / type:feature / priority:* / rejection:*"
  $DO_BOARD    && echo "  • Board:     Status normalized to Backlog/In Progress/Human Review/Done/Deferred; ids in .github/agent-loop.env"
  $DO_WORKFLOW && echo "  • Workflows: plan-dispatch (dispatch:plan) + agent-dispatch (dispatch:claude) + codex-dispatch (dispatch:codex) + openrouter-dispatch (dispatch:openrouter)"
  $DO_SECRETS  && echo "  • Secrets:   CLAUDE_CODE_OAUTH_TOKEN + OPENAI_API_KEY + OPENROUTER_API_KEY + PROJECTS_TOKEN (board write)"
  echo "  • Variables: explicit planner + per-provider executor model/effort (see above)"
  echo "  • Routing:   run /setup-agent-routing in Claude Code"
  echo ""
  echo "  How to drive it:"
  echo "    1. Put an issue in the board's Backlog column (Status field — not a label)."
  echo "    2. Apply dispatch:plan to prepare requirements and a decision-complete Implementation"
  echo "       Plan comment with revision, base SHA, requirements hash, and readiness; it lands in Human Review and"
  echo "       applies no execution gate. Approve it: move back to Backlog, then gate it."
  echo "    3. For a READY issue in Backlog, apply exactly one execution gate: codex, claude, or openrouter."
  echo "    4. Phase 1 (local):  run  /loop   to claim + work one issue (Claude)."
  echo "    5. Phase 2 (push): trusted gate-applier + eligible Backlog + current READY plan dispatch execution."
  echo "    6. PR publication -> different-provider frontier review + resolved findings + green required CI."
  echo "    7. Merge-ready only after those gates; Done only after merge and required deployment evidence."
  echo ""
  echo "  Full loop reference: .agents/memory/system/ai-dev-loop.md"
}

usage() {
  cat <<'USAGE'
setup-dev-loop.sh — provision the AI dev loop on a GitHub repo

Usage:
  setup-dev-loop.sh                     Set up the current repo
  setup-dev-loop.sh --repo owner/name   Target a specific repo
  setup-dev-loop.sh --project 7         Reuse an existing board number
  setup-dev-loop.sh --dry-run           Preview without changing anything

Options:
  --repo <owner/name>   Target repo (default: detected from the current remote)
  --project <number>    Reuse this board instead of creating/finding one
  --skip-labels         Do not migrate/create labels
  --skip-board          Do not provision the Projects board
  --skip-workflow       Do not install the dispatch workflows
  --skip-secrets        Do not touch the auth secrets
  --dry-run             Preview changes without executing
  --verbose             Show detailed output
  --help                Show this help

What it does:
  1. Migrates legacy labels in place, then creates the dispatch labels
     (claim:active, priority:*, rejection:N, dispatch:plan, dispatch:claude,
     dispatch:codex, dispatch:openrouter, type:feature, wontfix). The two
     status:* labels are deleted — status moves to the board.
  2. Provisions the Projects board: creates-or-reuses the project, normalizes
     its Status options to Backlog/In Progress/Human Review/Done/Deferred, and writes the board node
     ids to .github/agent-loop.env (non-secret).
  3. Installs the Phase-2 push workflows: plan-dispatch.yml (planning gate,
     dispatch:plan), agent-dispatch.yml (Claude lane, dispatch:claude),
     codex-dispatch.yml (Codex lane, dispatch:codex), and openrouter-dispatch.yml
     (OpenRouter lane, dispatch:openrouter), shared dispatch contract/guard, and
     the companion skill directories under .github/agent-skills/.
  4. Arms the auth secrets: CLAUDE_CODE_OAUTH_TOKEN (subscription OAuth),
     OPENAI_API_KEY (Codex lane), OPENROUTER_API_KEY (OpenRouter lane), and
     PROJECTS_TOKEN (project-scoped PAT for the board write — the default
     GITHUB_TOKEN cannot touch an org board).
  5. Prints explicit planner and executor runtime variables; no automatic fallback.
     Reviewer automation and protected-branch gates require separate provisioning.
  6. Points you at /setup-agent-routing for the per-repo routing block.

Examples:
  setup-dev-loop.sh
  setup-dev-loop.sh --repo shipshitdev/skills
  setup-dev-loop.sh --dry-run --skip-secrets
USAGE
}

require_option_value() {
  local flag="$1" value="${2-}"
  if [[ -z "$value" || "$value" == --* ]]; then
    err "Missing value for ${flag}"
    usage
    exit 1
  fi
}

# ============================================================================
# Main
# ============================================================================

main() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo)             require_option_value "$1" "${2-}"; REPO="$2"; shift 2 ;;
      --project)          require_option_value "$1" "${2-}"; PROJECT_NUMBER="$2"; shift 2 ;;
      --skip-labels)      DO_LABELS=false; shift ;;
      --skip-board)       DO_BOARD=false; shift ;;
      --skip-workflow)    DO_WORKFLOW=false; shift ;;
      --skip-workflows)   DO_WORKFLOW=false; shift ;;
      --skip-secrets)     DO_SECRETS=false; shift ;;
      --skip-secret)      DO_SECRETS=false; shift ;;
      --dry-run)          DRY_RUN=true; shift ;;
      --verbose)          VERBOSE=true; shift ;;
      --help|-h)          usage; exit 0 ;;
      *)                  err "Unknown option: $1"; usage; exit 1 ;;
    esac
  done

  require_gh
  resolve_repo

  $DRY_RUN && warn "DRY RUN — no changes will be made"
  info "Setting up the AI dev loop on ${REPO}"

  $DO_LABELS   && { migrate_labels; create_labels; }
  $DO_BOARD    && provision_board
  $DO_WORKFLOW && install_workflows
  $DO_SECRETS  && setup_secrets
  print_variables_step
  print_routing_step
  print_summary
}

main "$@"
