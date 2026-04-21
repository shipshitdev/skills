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

SKILLS_DIR="$REPO_ROOT/skills"

SKILL_NAME="${1:-}"

# Statistics
TOTAL_ISSUES=0
TOTAL_WARNINGS=0
TOTAL_SKILLS=0
SKILLS_WITH_ISSUES=0

# Skills that legitimately need limited platform references in subject matter
PLATFORM_EXEMPT_SKILLS=""

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
    if ! echo "$content" | grep -q "^---$"; then
        echo -e "  ${RED}✗${NC} Missing frontmatter (---)"
        return 1
    fi

    # Check for required fields
    if ! echo "$content" | grep -q "^name:"; then
        echo -e "  ${RED}✗${NC} Missing required 'name' field"
        ((issues++))
    fi

    if ! echo "$content" | grep -q "^description:"; then
        echo -e "  ${RED}✗${NC} Missing required 'description' field"
        ((issues++))
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
            ((warnings++))
        fi
    done <<< "$frontmatter"

    return $warnings
}

# Function to check for platform-specific tool references
check_tool_references() {
    local file="$1"
    local warnings=0

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    # Strip content inside PLATFORM-SPECIFIC markers before checking
    local content
    content=$(sed '/<!-- PLATFORM-SPECIFIC-START/,/<!-- PLATFORM-SPECIFIC-END/d' "$file")

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
        if echo "$content" | grep -qi "$pattern"; then
            local line_num
            line_num=$(grep -n -i "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Tool reference: '$pattern' (line $line_num)"
            ((warnings++))
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

    # Strip content inside PLATFORM-SPECIFIC markers before checking
    local content
    content=$(sed '/<!-- PLATFORM-SPECIFIC-START/,/<!-- PLATFORM-SPECIFIC-END/d' "$file")

    # Check for platform-name coupling in universal instructions.
    # Small CLI-specific notes are fine when isolated behind marker blocks.
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
        if echo "$content" | grep -q "$pattern"; then
            local line_num
            line_num=$(grep -n "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Platform coupling: '$pattern' (line $line_num)"
            ((warnings++))
        fi
    done

    return $warnings
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

    # Strip content inside PLATFORM-SPECIFIC markers before checking
    local content
    content=$(sed '/<!-- PLATFORM-SPECIFIC-START/,/<!-- PLATFORM-SPECIFIC-END/d' "$file")

    # These are literal strings to search for in file content, not shell paths
    # shellcheck disable=SC2088
    local path_patterns=(
        "~/.claude/"
        "~/.codex/"
        "~/.cursor/"
    )

    for pattern in "${path_patterns[@]}"; do
        if echo "$content" | grep -q "$pattern"; then
            local line_num
            line_num=$(grep -n "$pattern" "$file" | head -1 | cut -d: -f1)
            echo -e "  ${YELLOW}⚠${NC} Hardcoded path: '$pattern' (line $line_num)"
            ((warnings++))
        fi
    done

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

# Function to validate a single skill
validate_skill() {
    local skill_name="$1"
    local skill_issues=0
    local skill_warnings=0

    echo -e "${BLUE}Validating: $skill_name${NC}"

    local skill_file="$SKILLS_DIR/$skill_name/SKILL.md"
    if [[ -f "$skill_file" ]]; then
        check_frontmatter "$skill_file" || skill_issues=$?

        local frontmatter_warnings=0
        check_frontmatter_fields "$skill_file" || frontmatter_warnings=$?
        ((skill_warnings += frontmatter_warnings))

        # Platform-agnostic checks
        check_tool_references "$skill_file" || skill_warnings=$?

        local name_warnings=0
        check_platform_names "$skill_file" "$skill_name" || name_warnings=$?
        ((skill_warnings += name_warnings))

        local path_warnings=0
        check_platform_paths "$skill_file" "$skill_name" || path_warnings=$?
        ((skill_warnings += path_warnings))

        local line_warnings=0
        check_line_count "$skill_file" || line_warnings=$?
        ((skill_warnings += line_warnings))

        # Also check references/ directory
        if [[ -d "$SKILLS_DIR/$skill_name/references" ]]; then
            for ref_file in "$SKILLS_DIR/$skill_name/references/"*.md; do
                if [[ -f "$ref_file" ]]; then
                    local ref_warnings=0
                    check_tool_references "$ref_file" || ref_warnings=$?
                    ((skill_warnings += ref_warnings))

                    local ref_name_warnings=0
                    check_platform_names "$ref_file" "$skill_name" || ref_name_warnings=$?
                    ((skill_warnings += ref_name_warnings))

                    local ref_path_warnings=0
                    check_platform_paths "$ref_file" "$skill_name" || ref_path_warnings=$?
                    ((skill_warnings += ref_path_warnings))
                fi
            done
        fi
    else
        echo -e "  ${RED}✗${NC} SKILL.md missing"
        ((skill_issues++))
    fi

    if [[ $skill_issues -eq 0 ]] && [[ $skill_warnings -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC} Valid (Claude + Codex)"
    elif [[ $skill_issues -eq 0 ]]; then
        echo -e "  ${YELLOW}⚠${NC} Valid but has $skill_warnings compatibility warning(s)"
        ((SKILLS_WITH_ISSUES++))
        ((TOTAL_WARNINGS += skill_warnings))
    else
        ((SKILLS_WITH_ISSUES++))
        ((TOTAL_ISSUES += skill_issues))
        ((TOTAL_WARNINGS += skill_warnings))
    fi

    echo
    return 0
}

# Main validation logic
if [[ -n "$SKILL_NAME" ]]; then
    # Validate specific skill
    if [[ ! -d "$SKILLS_DIR/$SKILL_NAME" ]]; then
        echo -e "${RED}Error: Skill '$SKILL_NAME' not found${NC}"
        exit 1
    fi
    ((TOTAL_SKILLS++))
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
            ((TOTAL_SKILLS++))
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
