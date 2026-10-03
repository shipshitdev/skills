#!/bin/bash
#
# Validate Skills (Claude + Codex Check)
#
# Validates skills have required files, frontmatter, and avoid coupling
# that would break shared Claude Code + Codex usage.
#
# Usage:
#   ./scripts/validate-skill-sync.sh [skill-name]
#
# Examples:
#   ./scripts/validate-skill-sync.sh                    # Validate all skills
#   ./scripts/validate-skill-sync.sh accessibility      # Validate specific skill
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

SKILLS_DIR="${SKILLS_DIR_OVERRIDE:-$REPO_ROOT/skills}"
EXISTING_SKILLS="$(
    find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | while read -r skill_dir; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            basename "$skill_dir"
        fi
    done | sort
)"

SKILL_NAME="${1:-}"

# Statistics
TOTAL_ISSUES=0
TOTAL_WARNINGS=0
TOTAL_SKILLS=0
SKILLS_WITH_ISSUES=0

# Skills that legitimately need limited platform references in subject matter
PLATFORM_EXEMPT_SKILLS=""

# Skills with orchestration, local writes, or external side effects must declare
# their operating boundary so Claude-only frontmatter is not the only safety
# mechanism. Keep this list focused; add skills here when they become
# composable/action-oriented.
CONTRACT_REQUIRED_SKILLS="
agent-config-audit
agent-folder-init
codebase-advisor
deploy
deployment-composer
feature-intake
fullstack-workspace-init
github-address-comments
github-fix-ci
git-safety
landing-page-vercel
micro-landing-builder
project-init-orchestrator
release
rules-capture
scaffold
prd-task-creator
pstack
create-verification-skill
maintain-verification-skill
show-me-your-work
no-comments
arena
swarm
"

skill_exists() {
    local skill_name="$1"
    grep -Fxq "$skill_name" <<< "$EXISTING_SKILLS"
}

# Function to check frontmatter
check_frontmatter() {
    local file="$1"
    local issues=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local content
    content=$(cat "$file")

    # Check for frontmatter
    if ! grep -q "^---$" <<< "$content"; then
        echo -e "  ${RED}✗${NC} Missing frontmatter (---)"
        return 1
    fi

    # Check for required fields
    if ! grep -q "^name:" <<< "$content"; then
        echo -e "  ${RED}✗${NC} Missing required 'name' field"
        ((++issues))
    fi

    if ! grep -q "^description:" <<< "$content"; then
        echo -e "  ${RED}✗${NC} Missing required 'description' field"
        ((++issues))
    fi

    if grep -Eq '^description: [^>|"'"'"'].*: ' <<< "$content"; then
        echo -e "  ${RED}✗${NC} Plain description contains ': ' — quote it or use a folded block so YAML parsers do not skip the skill"
        ((++issues))
    fi

    return $issues
}

# Function to extract frontmatter body
get_frontmatter_block() {
    local file="$1"
    awk '
        NR == 1 && $0 == "---" { in_frontmatter = 1; next }
        in_frontmatter && $0 == "---" { exit }
        in_frontmatter { print }
    ' "$file"
}

# Function to check description length constraints documented in SKILL-STANDARDS.md
check_description_constraints() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local findings
    findings=$(python3 - "$file" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text()
if not text.startswith("---\n"):
    sys.exit(0)

end = text.find("\n---", 4)
if end == -1:
    sys.exit(0)

frontmatter = text[4:end]
lines = frontmatter.splitlines()

def scalar(key: str) -> str:
    for i, line in enumerate(lines):
        if not line.startswith(f"{key}:"):
            continue

        value = line.split(":", 1)[1].strip()
        if re.fullmatch(r"[>|][+-]?", value):
            parts = []
            for nxt in lines[i + 1:]:
                if nxt and not nxt.startswith((" ", "\t")):
                    break
                parts.append(nxt.strip())
            return " ".join(part for part in parts if part).strip()

        return value.strip().strip("\"'")
    return ""

description = scalar("description")
when_to_use = scalar("when_to_use")

if len(description) == 0:
    print("description is empty")
elif len(description) > 1024:
    print(f"description is {len(description)} chars (>1024)")

combined_len = len(description) + len(when_to_use)
if combined_len > 1536:
    print(f"description + when_to_use is {combined_len} chars (>1536)")
PY
)

    if [[ -n "$findings" ]]; then
        while IFS= read -r finding; do
            [[ -n "$finding" ]] || continue
            echo -e "  ${YELLOW}⚠${NC} $finding"
            ((++warnings))
        done <<< "$findings"
    fi

    return $warnings
}

# Function to check for unsupported top-level frontmatter fields
check_frontmatter_fields() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local frontmatter
    frontmatter=$(get_frontmatter_block "$file")

    if [[ -z "$frontmatter" ]]; then
        return 0
    fi

    local allowed_fields=(
        "name"
        "description"
        "license"
        "compatibility"
        "metadata"
        "allowed-tools"
        "disallowed-tools"
        "when_to_use"
        "disable-model-invocation"
        "user-invocable"
        "argument-hint"
        "model"
        "effort"
        "context"
        "agent"
        "hooks"
        "paths"
        "shell"
    )

    while IFS= read -r line; do
        [[ "$line" =~ ^[A-Za-z0-9_-]+: ]] || continue

        local field
        field="${line%%:*}"
        local is_allowed=0

        for allowed in "${allowed_fields[@]}"; do
            if [[ "$field" == "$allowed" ]]; then
                is_allowed=1
                break
            fi
        done

        if [[ $is_allowed -eq 0 ]]; then
            local line_num
            line_num=$(grep -n "^$field:" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Unsupported top-level frontmatter field: '$field' (line $line_num)"
            ((++warnings))
        fi

        # paths is documented but broken upstream (Claude Code issue #49835, as of
        # v2.1.84): skills with paths set become undiscoverable. Warn until fixed;
        # use a nested .claude/skills/ directory for monorepo scoping instead.
        if [[ "$field" == "paths" ]]; then
            local paths_line
            paths_line=$(grep -n "^paths:" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} 'paths' field is broken upstream (issue #49835) — skills with it set become undiscoverable; use nested .claude/skills/ instead (line $paths_line)"
            ((++warnings))
        fi
    done <<< "$frontmatter"

    return $warnings
}

# Validate repository-specific scalar/type rules that a line-oriented allowlist misses.
# These are hard schema errors: malformed YAML can make a skill silently undiscoverable.
check_frontmatter_types() {
    local file="$1"
    local issues=0
    local findings

    findings=$(python3 - "$file" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
lines = path.read_text().splitlines()
if not lines or lines[0] != "---":
    sys.exit(0)

try:
    end = lines.index("---", 1)
except ValueError:
    sys.exit(0)

frontmatter = lines[1:end]

for index, line in enumerate(frontmatter):
    if line.startswith("allowed-tools:"):
        value = line.split(":", 1)[1].strip()
        if not value or value.startswith(("[", "{")):
            print("allowed-tools must be a space-separated scalar, not a block/list")

metadata_start = next(
    (index for index, line in enumerate(frontmatter) if line == "metadata:"),
    None,
)
if metadata_start is None:
    sys.exit(0)

for index in range(metadata_start + 1, len(frontmatter)):
    line = frontmatter[index]
    if line and not line.startswith((" ", "\t")):
        break
    if not line.strip():
        continue

    match = re.match(r"^  ([A-Za-z0-9_-]+):\s*(.*)$", line)
    if not match:
        print("metadata values must be scalar strings, not nested lists/maps")
        continue

    key, value = match.groups()
    if key == "triggers":
        print("metadata.triggers is a no-op activation field; use description/when_to_use")
    if not value or value.startswith(("[", "{")):
        print(f"metadata.{key} must be a scalar string")
    if key in {"version", "tags"}:
        quoted = len(value) >= 2 and value[0] in {'"', "'"} and value[-1] == value[0]
        if not quoted:
            print(f"metadata.{key} must be a quoted string")
PY
)

    if [[ -n "$findings" ]]; then
        while IFS= read -r finding; do
            [[ -n "$finding" ]] || continue
            echo -e "  ${RED}✗${NC} $finding"
            ((++issues))
        done <<< "$findings"
    fi

    return $issues
}

# App/session execution parameters are recognized by some harnesses but forbidden by
# this library's execution boundary. Warn because prose/examples still require review.
filter_pstack_execution_protocol() {
    grep -vE '/pstack/scripts/runner/commands\.test\.ts:|/pstack/scripts/runner/commands\.ts:[0-9]+:[[:space:]]*return .model_reasoning_effort=[$][{]JSON[.]stringify[(]effort[)][}].;' || true
}

check_harness_execution_parameters() {
    local skill_dir="$1"
    local warnings=0
    local hits

    hits=$(grep -rInE --exclude-dir=node_modules \
        --include='SKILL.md' --include='*.md' --include='*.py' \
        --include='*.js' --include='*.ts' --include='*.sh' \
        '^(model|effort):|model:[[:space:]]*["'"'"']?(sonnet|opus|haiku|inherit)(["'"'"']|$)|effort:[[:space:]]*["'"'"']?(low|medium|high|xhigh|max)(["'"'"']|$)|CODEX_(MODEL|EFFORT)|model_reasoning_effort' \
        "$skill_dir" 2>/dev/null | filter_pstack_execution_protocol || true)

    if [[ -n "$hits" ]]; then
        while IFS= read -r hit; do
            [[ -n "$hit" ]] || continue
            echo -e "  ${YELLOW}⚠${NC} Harness-owned execution parameter in reusable content: $hit"
            ((++warnings))
        done <<< "$hits"
    fi

    return $warnings
}

# Mutating scripts and auto-approved Write/Edit tools require a body authorization
# gate. Engine discoverability does not grant permission to perform those writes.
check_side_effect_safety() {
    local file="$1"
    local skill_dir="$2"
    local warnings=0
    local findings

    findings=$(python3 - "$file" "$skill_dir" <<'PY'
import pathlib
import re
import sys

skill_file = pathlib.Path(sys.argv[1])
skill_dir = pathlib.Path(sys.argv[2])
text = skill_file.read_text()

frontmatter_end = text.find("\n---", 4)
frontmatter = text[4:frontmatter_end] if frontmatter_end != -1 else ""
body = text[frontmatter_end + 4:] if frontmatter_end != -1 else text

allowed_match = re.search(r"^allowed-tools:(.*(?:\n[ \t]+-[^\n]+)*)", frontmatter, re.M)
allowed_tools = allowed_match.group(0) if allowed_match else ""
mutating = bool(re.search(r"\b(Write|Edit)\b", allowed_tools))

script_pattern = re.compile(
    r"\.write_(?:text|bytes)\(|\.mkdir\(|\.unlink\(|rmtree\(|copy2?\(|"
    r"open\([^\n]+,\s*[\"'](?:w|a|x)",
)
for script_dir_name in ("scripts",):
    script_dir = skill_dir / script_dir_name
    if not script_dir.is_dir():
        continue
    for path in script_dir.rglob("*"):
        if "node_modules" in path.relative_to(script_dir).parts:
            continue
        if not path.is_file() or path.suffix not in {".py", ".js", ".ts", ".sh", ".mjs"}:
            continue
        try:
            script_text = path.read_text()
        except UnicodeDecodeError:
            continue
        if script_pattern.search(script_text):
            mutating = True
            break

if not mutating:
    sys.exit(0)

confirmation = re.search(
    r"^Confirmation Required:\s*\n(.*?)(?=^[A-Z][A-Za-z /]+:\s*$|^## )",
    body,
    re.M | re.S,
)
confirmation_text = confirmation.group(1).strip() if confirmation else ""
if not confirmation_text or re.fullmatch(r"[-*\s]*(none|nothing)[.\s]*", confirmation_text, re.I):
    print("side-effecting skill must declare an explicit Confirmation Required gate")
PY
)

    if [[ -n "$findings" ]]; then
        while IFS= read -r finding; do
            [[ -n "$finding" ]] || continue
            echo -e "  ${YELLOW}⚠${NC} $finding"
            ((++warnings))
        done <<< "$findings"
    fi

    return $warnings
}

# Hard gate: plugin.json must mirror SKILL.md metadata.version (SKILL.md is
# canonical) and must carry a real description — not a YAML block scalar
# marker ("|" / ">") that leaked in from a frontmatter copy.
check_plugin_manifest_sync() {
    local skill_dir="$1"
    local issues=0
    local plugin_json="$skill_dir/plugin.json"
    local skill_file="$skill_dir/SKILL.md"

    if [[ ! -f "$plugin_json" ]] || [[ ! -f "$skill_file" ]]; then
        return 0
    fi

    local findings
    findings=$(python3 - "$plugin_json" "$skill_file" <<'PY'
import json
import pathlib
import re
import sys

plugin_path = pathlib.Path(sys.argv[1])
skill_path = pathlib.Path(sys.argv[2])

try:
    data = json.loads(plugin_path.read_text())
except json.JSONDecodeError:
    sys.exit(0)  # reported by check_plugin_manifest

description = data.get("description", "")
if isinstance(description, str) and re.fullmatch(r"\s*[|>][+-]?\s*", description):
    print(f"plugin.json description is a YAML block marker ({description.strip()!r}), not text")

lines = skill_path.read_text().splitlines()
if not lines or lines[0].strip() != "---":
    sys.exit(0)
try:
    end = lines.index("---", 1)
except ValueError:
    sys.exit(0)

skill_version = None
in_metadata = False
for line in lines[1:end]:
    if line == "metadata:":
        in_metadata = True
        continue
    if in_metadata and line and not line.startswith((" ", "\t")):
        break
    if in_metadata:
        match = re.match(r"^  version:\s*[\"']?([^\"']*)[\"']?\s*$", line)
        if match:
            skill_version = match.group(1).strip()
            break

plugin_version = data.get("version")
if skill_version and isinstance(plugin_version, str) and plugin_version != skill_version:
    print(
        f"plugin.json version {plugin_version} != SKILL.md metadata.version {skill_version}"
        " (SKILL.md is canonical — sync plugin.json)"
    )
PY
)

    if [[ -n "$findings" ]]; then
        while IFS= read -r finding; do
            [[ -n "$finding" ]] || continue
            echo -e "  ${RED}✗${NC} $finding"
            ((++issues))
        done <<< "$findings"
    fi

    return $issues
}

# Function to check required metadata keys
check_metadata_fields() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local frontmatter
    frontmatter=$(get_frontmatter_block "$file")

    if [[ -z "$frontmatter" ]]; then
        return 0
    fi

    if ! grep -q "^metadata:$" <<< "$frontmatter"; then
        echo -e "  ${YELLOW}⚠${NC} Missing metadata block"
        return 1
    fi

    if ! awk '
        /^metadata:$/ { in_metadata = 1; next }
        in_metadata && /^[A-Za-z0-9_-]+:/ { in_metadata = 0 }
        in_metadata && /^  version: / { found = 1 }
        END { exit found ? 0 : 1 }
    ' <<< "$frontmatter"; then
        echo -e "  ${YELLOW}⚠${NC} Missing metadata.version"
        ((++warnings))
    fi

    if ! awk '
        /^metadata:$/ { in_metadata = 1; next }
        in_metadata && /^[A-Za-z0-9_-]+:/ { in_metadata = 0 }
        in_metadata && /^  tags: / { found = 1 }
        END { exit found ? 0 : 1 }
    ' <<< "$frontmatter"; then
        echo -e "  ${YELLOW}⚠${NC} Missing metadata.tags"
        ((++warnings))
    fi

    return $warnings
}

# Function to check for platform-specific tool references
check_tool_references() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local content
    content=$(cat "$file")

    # Check for Claude-specific tool references (match as standalone tool names)
    local tool_patterns=(
        "the Skill tool"
        "the Read tool"
        "the Edit tool"
        "the Bash tool"
        "the Glob tool"
        "the Grep tool"
        "the Agent tool"
        "using Skill tool"
        "Use Read tool"
        "Use Bash tool"
        "Use Edit tool"
        "Use Glob tool"
        "Use Grep tool"
    )

    for pattern in "${tool_patterns[@]}"; do
        if grep -qi "$pattern" <<< "$content"; then
            local line_num
            line_num=$(grep -n -i "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Tool reference: '$pattern' (line $line_num)"
            ((++warnings))
        fi
    done

    return $warnings
}

# Function to check for platform-name coupling
check_platform_names() {
    local file="$1"
    local skill_name="$2"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    # Skip exempt skills
    for exempt in $PLATFORM_EXEMPT_SKILLS; do
        if [[ "$skill_name" == "$exempt" ]]; then
            return 0
        fi
    done

    local content
    content=$(cat "$file")

    # Check for platform-name coupling in universal instructions. Platform-specific
    # entry surfaces live outside canonical skill bodies; comments do not isolate them.
    local platform_patterns=(
        "Claude will"
        "Claude reads"
        "Claude determines"
        "This skill enables Claude"
        "Claude should use"
        "Ask Claude to:"
        "^Claude:$"
        "another Claude instance"
        "Codex will"
        "Codex reads"
        "Codex determines"
    )

    for pattern in "${platform_patterns[@]}"; do
        if grep -q "$pattern" <<< "$content"; then
            local line_num
            line_num=$(grep -n "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Platform coupling: '$pattern' (line $line_num)"
            ((++warnings))
        fi
    done

    return $warnings
}

# Function to check for concrete/version-pinned model names.
# Skills are model-agnostic playbooks — the harness supplies the model. Orchestrators
# may name capability tiers ("strongest tier") in prose but never a concrete ID.
# These are hard errors: version-pinned IDs and bare model-family names used as
# routing keys are never legitimate in a portable public skill. Capability-tier
# prose remains valid; concrete model mappings belong to harness configuration.
# These five files parse provider receipts or test explicit caller-supplied values.
# They contain protocol samples, never model defaults. All other runtime files and
# every prompt/config surface remain subject to the ordinary model-policy check.
filter_pstack_protocol_fixtures() {
    grep -vE '/pstack/scripts/runner/(model-aliases\.ts|commands\.test\.ts|run\.test\.ts|cli\.test\.ts|parse-output\.test\.ts):' || true
}

check_model_references() {
    local skill_dir="$1"
    local warnings=0

    if [[ ! -d "$skill_dir" ]]; then
        return 0
    fi

    # High-confidence stale patterns: family+digit and tier+version model IDs.
    # (Dated snapshots like -20250219 always co-occur with claude-N, so covered.)
    local model_re='claude-[0-9]|claude-(opus|sonnet|haiku)-|gpt-[0-9]|gemini-[0-9]'

    local hits
    hits=$(grep -rIniE "$model_re" --exclude-dir=node_modules \
        --include='SKILL.md' --include='*.md' --include='*.py' \
        --include='*.js' --include='*.ts' --include='*.sh' \
        "$skill_dir" 2>/dev/null | filter_pstack_protocol_fixtures || true)

    if [[ -n "$hits" ]]; then
        while IFS= read -r hit; do
            echo -e "  ${RED}✗${NC} Concrete model name (harness owns model selection): ${hit}"
            ((++warnings))
        done <<< "$hits"
    fi

    # Bare tier names outside a model assignment — a routing key in prose pins
    # the skill to one vendor's tier vocabulary. The tier→model mapping belongs
    # in the per-repo routing block, not in the skill.
    local bare_tier_hits
    bare_tier_hits=$(grep -rInEw 'sonnet|opus|haiku' --exclude-dir=node_modules \
        --include='SKILL.md' --include='*.md' --include='*.py' \
        --include='*.js' --include='*.ts' --include='*.sh' \
        "$skill_dir" 2>/dev/null \
        | grep -viE 'model["'"'"']?\s*[:=]\s*["'"'"']?(sonnet|opus|haiku)' \
        | grep -vE "$model_re" | filter_pstack_protocol_fixtures || true)

    if [[ -n "$bare_tier_hits" ]]; then
        while IFS= read -r hit; do
            echo -e "  ${RED}✗${NC} Bare model tier as routing key (use a capability tier in prose; concrete mapping lives in the repo routing block): ${hit}"
            ((++warnings))
        done <<< "$bare_tier_hits"
    fi

    return $warnings
}

# Commands and authoring resources are reusable prompt surfaces too. Concrete model
# IDs are hard errors there just as they are inside a skill directory.
check_public_concrete_models() {
    local issues=0
    local model_re='claude-[0-9]|claude-(opus|sonnet|haiku)-|gpt-[0-9]|gemini-[0-9]'
    local roots=()
    local root

    for root in "$REPO_ROOT/commands" "$REPO_ROOT/prompts" "$REPO_ROOT/resources"; do
        [[ -d "$root" ]] && roots+=("$root")
    done

    [[ ${#roots[@]} -gt 0 ]] || return 0

    local hits
    hits=$(grep -rIniE "$model_re" --exclude-dir=node_modules \
        --include='*.md' --include='*.py' --include='*.js' \
        --include='*.ts' --include='*.sh' "${roots[@]}" 2>/dev/null || true)
    if [[ -n "$hits" ]]; then
        while IFS= read -r hit; do
            [[ -n "$hit" ]] || continue
            echo -e "${RED}✗${NC} Concrete model name in public prompt/template: $hit"
            ((++issues))
        done <<< "$hits"
    fi

    return $issues
}

# Report app-owned execution selection in commands and templates. These are warnings
# so maintainers can distinguish an actual directive from a discussion of the field.
check_public_execution_parameters() {
    local warnings=0
    local roots=()
    local root

    for root in "$REPO_ROOT/commands" "$REPO_ROOT/prompts" "$REPO_ROOT/resources"; do
        [[ -d "$root" ]] && roots+=("$root")
    done

    [[ ${#roots[@]} -gt 0 ]] || return 0

    local hits
    hits=$(grep -rInE --exclude-dir=node_modules \
        --include='*.md' --include='*.py' --include='*.js' \
        --include='*.ts' --include='*.sh' \
        'CODEX_(MODEL|EFFORT)|model_reasoning_effort|^(model|effort):[[:space:]]*(sonnet|opus|haiku|inherit|low|medium|high|xhigh|max)' \
        "${roots[@]}" 2>/dev/null || true)
    if [[ -n "$hits" ]]; then
        while IFS= read -r hit; do
            [[ -n "$hit" ]] || continue
            echo -e "${YELLOW}⚠${NC} Harness-owned execution parameter in public prompt/template: $hit"
            ((++warnings))
        done <<< "$hits"
    fi

    return $warnings
}

# Reject inert Codex repository surfaces and positive documentation claims that
# would cause scaffolds or contributors to recreate them.
check_supported_codex_surfaces() {
    local issues=0

    if [[ -e "$REPO_ROOT/.codex/instructions.md" ]]; then
        echo -e "${RED}✗${NC} Unsupported Codex instruction surface: .codex/instructions.md"
        ((++issues))
    fi
    if [[ -e "$REPO_ROOT/.codex/commands" ]]; then
        echo -e "${RED}✗${NC} Unsupported Codex command surface: .codex/commands"
        ((++issues))
    fi

    local roots=()
    local candidate
    for candidate in \
        "$REPO_ROOT/README.md" \
        "$REPO_ROOT/AGENTS.md" \
        "$REPO_ROOT/.agents" \
        "$REPO_ROOT/resources" \
        "$SKILLS_DIR"; do
        [[ -e "$candidate" ]] && roots+=("$candidate")
    done

    local claims
    claims=$(grep -rInE --exclude-dir=node_modules \
        --include='*.md' \
        '(\.codex/instructions\.md|\.codex/commands)' \
        "${roots[@]}" 2>/dev/null \
        | grep -viE '(do not|does not|don.t|never|unsupported|inert|deprecated|must not|cannot|no )' \
        || true)

    if [[ -n "$claims" ]]; then
        while IFS= read -r claim; do
            [[ -n "$claim" ]] || continue
            echo -e "${RED}✗${NC} Unsupported Codex path claim: $claim"
            ((++issues))
        done <<< "$claims"
    fi

    return $issues
}

# Ensure generated count and layout claims match the canonical catalog sources.
check_catalog_summary() {
    local output
    if ! output=$(bun "$REPO_ROOT/scripts/generate-catalog-summary.js" --check 2>&1); then
        echo -e "${RED}✗${NC} Generated catalog facts are stale"
        while IFS= read -r line; do
            [[ -n "$line" ]] && echo "  $line"
        done <<< "$output"
        return 1
    fi
    return 0
}

# The removed installer had destructive restore behavior and a stale hardcoded catalog.
check_legacy_installer_retired() {
    if [[ -e "$REPO_ROOT/scripts/install-skills.sh" ]]; then
        echo -e "${RED}✗${NC} Retired legacy installer returned: scripts/install-skills.sh"
        return 1
    fi
    return 0
}

# Function to check for hardcoded platform paths
check_platform_paths() {
    local file="$1"
    local skill_name="${2:-}"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    # Skip exempt skills
    for exempt in $PLATFORM_EXEMPT_SKILLS; do
        if [[ "$skill_name" == "$exempt" ]]; then
            return 0
        fi
    done

    local content
    content=$(cat "$file")

    # These are literal strings to search for in file content, not shell paths
    # shellcheck disable=SC2088
    local path_patterns=(
        "~/.claude/"
        "~/.codex/"
        "~/.cursor/"
    )

    for pattern in "${path_patterns[@]}"; do
        if grep -q "$pattern" <<< "$content"; then
            local line_num
            line_num=$(grep -n "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Hardcoded path: '$pattern' (line $line_num)"
            ((++warnings))
        fi
    done

    return $warnings
}

# HTML comments do not hide instructions from a harness. Canonical skills and their
# bundled resources must never rely on PLATFORM-SPECIFIC marker blocks.
check_platform_markers() {
    local skill_dir="$1"
    local issues=0
    local hits

    hits=$(grep -rInF --exclude-dir=node_modules --include='*.md' 'PLATFORM-SPECIFIC-' "$skill_dir" 2>/dev/null || true)
    if [[ -n "$hits" ]]; then
        while IFS= read -r hit; do
            [[ -n "$hit" ]] || continue
            echo -e "  ${RED}✗${NC} Inert platform marker in canonical skill content: $hit"
            ((++issues))
        done <<< "$hits"
    fi

    return $issues
}

# Validate three concrete adapter patterns kept outside public skill bodies. These
# checks prove the repository adapters route to shared sources instead of copying
# incompatible platform instructions into canonical skills.
validate_adapter_examples() {
    local issues=0

    if [[ ! -L "$REPO_ROOT/.claude/skills" ]] ||
        [[ "$(readlink "$REPO_ROOT/.claude/skills")" != "../.agents/skills" ]] ||
        [[ ! -L "$REPO_ROOT/.codex/skills" ]] ||
        [[ "$(readlink "$REPO_ROOT/.codex/skills")" != "../.agents/skills" ]]; then
        echo -e "${RED}✗${NC} Platform loader adapters must link to ../.agents/skills"
        ((++issues))
    fi

    if ! grep -Fq "Use the \`review-dispatch\` skill." "$REPO_ROOT/commands/review.md"; then
        echo -e "${RED}✗${NC} commands/review.md no longer routes to review-dispatch"
        ((++issues))
    fi

    if [[ ! -f "$REPO_ROOT/AGENTS.md" ]] ||
        ! grep -Fq '# Skills Repo — Agent Instructions' "$REPO_ROOT/AGENTS.md"; then
        echo -e "${RED}✗${NC} Codex project-instruction adapter AGENTS.md is missing"
        ((++issues))
    fi

    return $issues
}

# Commands are user front doors: the picker needs a description, the model must not
# auto-run them, and `/<name> help` must print Usage instead of starting the workflow.
check_command_surfaces() {
    local issues=0
    local file name frontmatter

    for file in "$REPO_ROOT"/commands/*.md; do
        [[ -f "$file" ]] || continue
        name=$(basename "$file" .md)

        if [[ "$(head -n 1 "$file")" != "---" ]]; then
            echo -e "${RED}✗${NC} commands/$name.md: missing frontmatter"
            ((++issues))
            continue
        fi

        frontmatter=$(awk 'NR == 1 { next } /^---$/ { exit } { print }' "$file")
        if ! grep -q '^description: ' <<< "$frontmatter"; then
            echo -e "${RED}✗${NC} commands/$name.md: frontmatter missing description"
            ((++issues))
        fi
        if ! grep -q '^disable-model-invocation: true$' <<< "$frontmatter"; then
            echo -e "${RED}✗${NC} commands/$name.md: frontmatter missing disable-model-invocation: true"
            ((++issues))
        fi
        if ! grep -q '^## Usage$' "$file"; then
            echo -e "${RED}✗${NC} commands/$name.md: missing ## Usage section"
            ((++issues))
        fi
        if ! grep -Fq "\`/$name help\` prints this Usage block and stops without running anything." "$file"; then
            echo -e "${RED}✗${NC} commands/$name.md: missing the standard /$name help line"
            ((++issues))
        fi
    done

    return $issues
}

# Function to check for external skill handoffs
check_external_handoffs() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local patterns=(
        "Complementary Skills (External)"
        "/plugin marketplace add"
        "github.com/coreyhaines31/marketingskills"
        "github.com/trailofbits/skills"
        "github.com/resend/resend-skills"
    )

    for pattern in "${patterns[@]}"; do
        if grep -Fq "$pattern" "$file"; then
            local line_num
            line_num=$(grep -n -F "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} External skill handoff: '$pattern' (line $line_num)"
            ((++warnings))
        fi
    done

    return $warnings
}

# Function to check for missing local skill references in routing sections
check_missing_skill_references() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    while IFS=: read -r line_num ref; do
        [[ -n "$ref" ]] || continue

        if ! skill_exists "$ref"; then
            echo -e "  ${YELLOW}⚠${NC} Missing local skill reference: '$ref' (line $line_num)"
            ((++warnings))
        fi
    done < <(
        python3 - "$file" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
patterns = [
    re.compile(
        r"\b(?:apply|run|use|invoke)\s+(?:the\s+)?"
        r"\x60([a-z0-9]+(?:-[a-z0-9]+)+)\x60\s+skill\b"
    ),
    re.compile(r"\b(?:the|existing|installed)\s+\x60([a-z0-9]+(?:-[a-z0-9]+)+)\x60\s+skill\b"),
    re.compile(r"^\s*-\s+\x60([a-z0-9]+(?:-[a-z0-9]+)+)\x60\s+(?:for|when|to)\b"),
    re.compile(r"→\s*\x60([a-z0-9]+(?:-[a-z0-9]+)+)\x60\s*$"),
    re.compile(r"Use @([a-z0-9]+(?:-[a-z0-9]+)+)\s+skill\b"),
]

in_code_fence = False
in_frontmatter = False
in_delegates = False
for lineno, line in enumerate(path.read_text().splitlines(), 1):
    if lineno == 1 and line == "---":
        in_frontmatter = True
        continue
    if in_frontmatter:
        if line == "---":
            in_frontmatter = False
        continue
    if line.lstrip().startswith(chr(96) * 3):
        in_code_fence = not in_code_fence
        continue
    if in_code_fence:
        continue

    if line == "Delegates To:":
        in_delegates = True
    elif line.startswith("## ") or re.match(r"^[A-Z][A-Za-z /]+:$", line):
        in_delegates = False

    for index, pattern in enumerate(patterns):
        if index == 2 and not in_delegates:
            continue
        match = pattern.search(line)
        if match:
            print(f"{lineno}:{match.group(1)}")
PY
    )

    return $warnings
}

# Function to check composable/action skills declare a safety contract
check_contract_requirements() {
    local file="$1"
    local skill_name="$2"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local requires_contract=0

    for required in $CONTRACT_REQUIRED_SKILLS; do
        if [[ "$skill_name" == "$required" ]]; then
            requires_contract=1
            break
        fi
    done

    if grep -q "^allowed-tools:" "$file"; then
        requires_contract=1
    fi

    if [[ $requires_contract -eq 0 ]]; then
        return 0
    fi

    if ! grep -q "^## Contract$" "$file"; then
        echo -e "  ${YELLOW}⚠${NC} Missing ## Contract section for composable/action skill"
        return 1
    fi

    local labels=(
        "Inputs:"
        "Outputs:"
        "Creates/Modifies:"
        "External Side Effects:"
        "Confirmation Required:"
        "Delegates To:"
    )

    for label in "${labels[@]}"; do
        if ! grep -q "^$label$" "$file"; then
            echo -e "  ${YELLOW}⚠${NC} Contract missing label: '$label'"
            ((++warnings))
        fi
    done

    return $warnings
}

# Function to check skill-local plugin manifest exists for distribution
check_plugin_manifest() {
    local skill_dir="$1"
    local warnings=0
    local plugin_json="$skill_dir/plugin.json"

    if [[ ! -f "$plugin_json" ]]; then
        echo -e "  ${YELLOW}⚠${NC} Missing plugin.json manifest"
        return 1
    fi

    local findings
    findings=$(python3 - "$plugin_json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except json.JSONDecodeError as exc:
    print(f"plugin.json is invalid JSON: {exc}")
    sys.exit(0)

description = data.get("description", "")
if not isinstance(description, str) or not description.strip():
    print("plugin.json description is empty")
elif len(description) > 100:
    print(f"plugin.json description is {len(description)} chars (>100)")
PY
)

    if [[ -n "$findings" ]]; then
        while IFS= read -r finding; do
            [[ -n "$finding" ]] || continue
            echo -e "  ${YELLOW}⚠${NC} $finding"
            ((++warnings))
        done <<< "$findings"
    fi

    return $warnings
}

# Function to check SKILL.md line count
check_line_count() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local lines
    lines=$(wc -l < "$file")
    if [[ $lines -gt 500 ]]; then
        echo -e "  ${YELLOW}⚠${NC} SKILL.md is $lines lines (recommended: <500)"
        return 1
    fi

    return 0
}

# Function to check reference directory naming
check_reference_directory() {
    local skill_dir="$1"

    if [[ -d "$skill_dir/reference" ]]; then
        echo -e "  ${YELLOW}⚠${NC} Non-standard reference directory: use 'references/' instead of 'reference/'"
        return 1
    fi

    return 0
}

# Function to check upstream provenance hygiene for externally-derived skills.
# Only skills that declare metadata.source are subject to these checks; in-house
# skills (no source) are exempt and pass silently. This keeps the upstream
# reference + last-synced date honest so drift against the original author is
# visible (see .agents/memory/system/upstream-tracking.md).
check_provenance() {
    local file="$1"
    local skill_dir="$2"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    local frontmatter
    frontmatter=$(get_frontmatter_block "$file")

    if [[ -z "$frontmatter" ]]; then
        return 0
    fi

    local source_val
    source_val=$(awk '
        /^metadata:$/ { in_metadata = 1; next }
        in_metadata && /^[A-Za-z0-9_-]+:/ { in_metadata = 0 }
        in_metadata && /^  source: / { sub(/^  source: /, ""); print; exit }
    ' <<< "$frontmatter")

    # No source declared -> in-house skill, provenance not required.
    if [[ -z "$source_val" ]]; then
        return 0
    fi

    # 1. README.md must carry an ## Upstream section documenting the source.
    local readme="$skill_dir/README.md"
    if [[ ! -f "$readme" ]] || ! grep -q "^## Upstream$" "$readme"; then
        echo -e "  ${YELLOW}⚠${NC} metadata.source set but README.md has no '## Upstream' section"
        ((++warnings))
    fi

    # 2. last_synced must be present.
    local synced
    synced=$(awk '
        /^metadata:$/ { in_metadata = 1; next }
        in_metadata && /^[A-Za-z0-9_-]+:/ { in_metadata = 0 }
        in_metadata && /^  last_synced: / { sub(/^  last_synced: /, ""); print; exit }
    ' <<< "$frontmatter" | tr -d "\"'" | xargs)

    if [[ -z "$synced" ]]; then
        echo -e "  ${YELLOW}⚠${NC} metadata.source set but metadata.last_synced missing"
        ((++warnings))
        return $warnings
    fi

    # 3. Warn when last_synced is malformed or older than 90 days (re-check upstream).
    local age_days
    age_days=$(python3 -c '
import sys, datetime
try:
    d = datetime.date.fromisoformat(sys.argv[1].strip())
except ValueError:
    sys.exit(0)
print((datetime.date.today() - d).days)
' "$synced" 2>/dev/null || true)

    if [[ -z "$age_days" ]]; then
        echo -e "  ${YELLOW}⚠${NC} metadata.last_synced is not an ISO date (YYYY-MM-DD): '$synced'"
        ((++warnings))
    elif [[ "$age_days" -gt 90 ]]; then
        echo -e "  ${YELLOW}⚠${NC} Upstream not re-checked in $age_days days (>90); diff against metadata.source and bump last_synced"
        ((++warnings))
    fi

    return $warnings
}

check_skill_composition() {
    local skill_name="$1"
    local output
    local issues=0
    if output=$(python3 "$SCRIPT_DIR/check-skill-composition.py" "$SKILLS_DIR" "$skill_name" 2>&1); then
        return 0
    fi
    while IFS= read -r finding; do
        [[ -n "$finding" ]] || continue
        echo -e "  ${RED}✗${NC} $finding"
        ((++issues))
    done <<< "$output"
    [[ $issues -gt 0 ]] || issues=1
    return "$issues"
}

# Function to validate a single skill
validate_skill() {
    local skill_name="$1"
    local skill_issues=0
    local skill_warnings=0

    echo -e "${BLUE}Validating: $skill_name${NC}"

    local skill_file="$SKILLS_DIR/$skill_name/SKILL.md"
    if [[ -f "$skill_file" ]]; then
        check_frontmatter "$skill_file" || skill_issues=$?

        local type_issues=0
        check_frontmatter_types "$skill_file" || type_issues=$?
        ((skill_issues += type_issues, 1))

        local description_warnings=0
        check_description_constraints "$skill_file" || description_warnings=$?
        ((skill_warnings += description_warnings, 1))

        local frontmatter_warnings=0
        check_frontmatter_fields "$skill_file" || frontmatter_warnings=$?
        ((skill_warnings += frontmatter_warnings, 1))

        local metadata_warnings=0
        check_metadata_fields "$skill_file" || metadata_warnings=$?
        ((skill_warnings += metadata_warnings, 1))

        local provenance_warnings=0
        check_provenance "$skill_file" "$SKILLS_DIR/$skill_name" || provenance_warnings=$?
        ((skill_warnings += provenance_warnings, 1))

        local model_issues=0
        check_model_references "$SKILLS_DIR/$skill_name" || model_issues=$?
        ((skill_issues += model_issues, 1))

        local execution_warnings=0
        check_harness_execution_parameters "$SKILLS_DIR/$skill_name" || execution_warnings=$?
        ((skill_warnings += execution_warnings, 1))

        local side_effect_warnings=0
        check_side_effect_safety "$skill_file" "$SKILLS_DIR/$skill_name" || side_effect_warnings=$?
        ((skill_warnings += side_effect_warnings, 1))

        local marker_issues=0
        check_platform_markers "$SKILLS_DIR/$skill_name" || marker_issues=$?
        ((skill_issues += marker_issues, 1))

        # Platform-agnostic checks
        local tool_warnings=0
        check_tool_references "$skill_file" || tool_warnings=$?
        ((skill_warnings += tool_warnings, 1))

        local name_warnings=0
        check_platform_names "$skill_file" "$skill_name" || name_warnings=$?
        ((skill_warnings += name_warnings, 1))

        local path_warnings=0
        check_platform_paths "$skill_file" "$skill_name" || path_warnings=$?
        ((skill_warnings += path_warnings, 1))

        local handoff_warnings=0
        check_external_handoffs "$skill_file" || handoff_warnings=$?
        ((skill_warnings += handoff_warnings, 1))

        local reference_warnings=0
        check_missing_skill_references "$skill_file" || reference_warnings=$?
        ((skill_warnings += reference_warnings, 1))

        local composition_issues=0
        check_skill_composition "$skill_name" || composition_issues=$?
        ((skill_issues += composition_issues, 1))

        local contract_warnings=0
        check_contract_requirements "$skill_file" "$skill_name" || contract_warnings=$?
        ((skill_warnings += contract_warnings, 1))

        local line_warnings=0
        check_line_count "$skill_file" || line_warnings=$?
        ((skill_warnings += line_warnings, 1))

        local reference_dir_warnings=0
        check_reference_directory "$SKILLS_DIR/$skill_name" || reference_dir_warnings=$?
        ((skill_warnings += reference_dir_warnings, 1))

        local plugin_warnings=0
        check_plugin_manifest "$SKILLS_DIR/$skill_name" || plugin_warnings=$?
        ((skill_warnings += plugin_warnings, 1))

        local plugin_sync_issues=0
        check_plugin_manifest_sync "$SKILLS_DIR/$skill_name" || plugin_sync_issues=$?
        ((skill_issues += plugin_sync_issues, 1))

        # Also check references/ directory
        if [[ -d "$SKILLS_DIR/$skill_name/references" ]]; then
            for ref_file in "$SKILLS_DIR/$skill_name/references/"*.md; do
                if [[ -f "$ref_file" ]]; then
                    local ref_warnings=0
                    check_tool_references "$ref_file" || ref_warnings=$?
                    ((skill_warnings += ref_warnings, 1))

                    local ref_name_warnings=0
                    check_platform_names "$ref_file" "$skill_name" || ref_name_warnings=$?
                    ((skill_warnings += ref_name_warnings, 1))

                    local ref_path_warnings=0
                    check_platform_paths "$ref_file" "$skill_name" || ref_path_warnings=$?
                    ((skill_warnings += ref_path_warnings, 1))

                    local ref_handoff_warnings=0
                    check_external_handoffs "$ref_file" || ref_handoff_warnings=$?
                    ((skill_warnings += ref_handoff_warnings, 1))
                fi
            done
        fi
    else
        echo -e "  ${RED}✗${NC} SKILL.md missing"
        ((++skill_issues))
    fi

    if [[ $skill_issues -eq 0 ]] && [[ $skill_warnings -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC} Valid (Claude + Codex)"
    elif [[ $skill_issues -eq 0 ]]; then
        echo -e "  ${YELLOW}⚠${NC} Valid but has $skill_warnings compatibility warning(s)"
        ((++SKILLS_WITH_ISSUES))
        ((TOTAL_WARNINGS += skill_warnings, 1))
    else
        ((++SKILLS_WITH_ISSUES))
        ((TOTAL_ISSUES += skill_issues, 1))
        ((TOTAL_WARNINGS += skill_warnings, 1))
    fi

    echo
    return 0
}

# Validate every reusable prompt surface before canonical skill content.
public_model_issues=0
check_public_concrete_models || public_model_issues=$?
((TOTAL_ISSUES += public_model_issues, 1))

public_execution_warnings=0
check_public_execution_parameters || public_execution_warnings=$?
((TOTAL_WARNINGS += public_execution_warnings, 1))

codex_surface_issues=0
check_supported_codex_surfaces || codex_surface_issues=$?
((TOTAL_ISSUES += codex_surface_issues, 1))

catalog_issues=0
check_catalog_summary || catalog_issues=$?
((TOTAL_ISSUES += catalog_issues, 1))

installer_issues=0
check_legacy_installer_retired || installer_issues=$?
((TOTAL_ISSUES += installer_issues, 1))

# Validate external adapter examples before canonical skill content.
adapter_issues=0
validate_adapter_examples || adapter_issues=$?
((TOTAL_ISSUES += adapter_issues, 1))

command_issues=0
check_command_surfaces || command_issues=$?
((TOTAL_ISSUES += command_issues, 1))

# Check live public entry points once, including installer and bundle membership.
if ! python3 "$SCRIPT_DIR/check-skill-composition.py" "$SKILLS_DIR" --catalog; then
    ((++TOTAL_ISSUES))
fi

# Main validation logic
if [[ -n "$SKILL_NAME" ]]; then
    # Validate specific skill
    if [[ ! -d "$SKILLS_DIR/$SKILL_NAME" ]]; then
        echo -e "${RED}Error: Skill '$SKILL_NAME' not found${NC}"
        exit 1
    fi
    ((++TOTAL_SKILLS))
    validate_skill "$SKILL_NAME"
else
    # Validate all skills
    echo -e "${BLUE}Validating all skills (Claude + Codex check)...${NC}"
    echo

    for skill_dir in "$SKILLS_DIR"/*/; do
        if [[ -d "$skill_dir" ]]; then
            if [[ -z "$(find "$skill_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
                continue
            fi
            skill_name=$(basename "$skill_dir")
            ((++TOTAL_SKILLS))
            validate_skill "$skill_name"
        fi
    done
fi

# Summary
echo -e "${BLUE}=== Validation Summary ===${NC}"
echo "Total skills checked: $TOTAL_SKILLS"
echo "Skills with issues: $SKILLS_WITH_ISSUES"
echo "Errors (missing files/frontmatter): $TOTAL_ISSUES"
echo "Warnings (compatibility issues): $TOTAL_WARNINGS"
echo

if [[ $TOTAL_ISSUES -eq 0 ]] && [[ $TOTAL_WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ All skills validated for shared Claude Code + Codex use.${NC}"
    exit 0
elif [[ $TOTAL_ISSUES -eq 0 ]]; then
    echo -e "${YELLOW}⚠ No errors, but $TOTAL_WARNINGS compatibility warning(s) found.${NC}"
    echo -e "${YELLOW}  Review warnings above and update skills for shared Claude Code + Codex usage.${NC}"
    exit 0
else
    echo -e "${RED}✗ $TOTAL_ISSUES error(s) found. Fix these before publishing.${NC}"
    exit 1
fi
