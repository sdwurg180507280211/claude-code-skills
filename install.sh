#!/bin/bash
# =============================================================================
# Claude Code Skills - One-click Installer
# =============================================================================
# This script installs Claude Code custom skills to ~/.claude/skills/
#
# Usage:
#   ./install.sh              # Install all skills
#   ./install.sh spec-mode    # Install a specific skill
#   ./install.sh --list       # List available skills
#   ./install.sh --uninstall  # Remove all installed skills
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$HOME/.claude/skills"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Available skills
AVAILABLE_SKILLS=("spec-mode" "chrome-devtools" "github-kb" "skill-creator")

print_banner() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Claude Code Skills Installer             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
    echo ""
}

list_skills() {
    echo -e "${BLUE}Available skills:${NC}"
    echo ""
    for skill in "${AVAILABLE_SKILLS[@]}"; do
        local desc=""
        if [ -f "$SKILLS_SRC/$skill/SKILL.md" ]; then
            desc=$(grep '^description:' "$SKILLS_SRC/$skill/SKILL.md" | head -1 | sed 's/^description: //')
            # Truncate long descriptions
            if [ ${#desc} -gt 80 ]; then
                desc="${desc:0:77}..."
            fi
        fi

        # Check if installed
        if [ -d "$SKILLS_DST/$skill" ]; then
            echo -e "  ${GREEN}✓${NC} ${YELLOW}$skill${NC} (installed)"
        else
            echo -e "  ○ ${YELLOW}$skill${NC}"
        fi
        if [ -n "$desc" ]; then
            echo -e "    $desc"
        fi
        echo ""
    done
}

install_skill() {
    local skill=$1
    local src="$SKILLS_SRC/$skill"
    local dst="$SKILLS_DST/$skill"

    if [ ! -d "$src" ]; then
        echo -e "${RED}Error: Skill '$skill' not found in $SKILLS_SRC${NC}"
        return 1
    fi

    # Create destination directory
    mkdir -p "$dst"

    # Copy all files
    cp -r "$src"/* "$dst/"

    echo -e "  ${GREEN}✓${NC} Installed: ${YELLOW}$skill${NC} → $dst"
}

uninstall_skills() {
    echo -e "${YELLOW}Uninstalling all skills...${NC}"
    echo ""
    for skill in "${AVAILABLE_SKILLS[@]}"; do
        local dst="$SKILLS_DST/$skill"
        if [ -d "$dst" ]; then
            rm -rf "$dst"
            echo -e "  ${RED}✗${NC} Removed: ${YELLOW}$skill${NC}"
        fi
    done
    echo ""
    echo -e "${GREEN}Done! All skills have been uninstalled.${NC}"
}

# Main logic
print_banner

case "${1:-}" in
    --list|-l)
        list_skills
        ;;
    --uninstall|-u)
        uninstall_skills
        ;;
    --help|-h)
        echo "Usage:"
        echo "  ./install.sh              Install all skills"
        echo "  ./install.sh <skill-name> Install a specific skill"
        echo "  ./install.sh --list       List available skills"
        echo "  ./install.sh --uninstall  Remove all installed skills"
        echo "  ./install.sh --help       Show this help"
        echo ""
        echo "Available skills: ${AVAILABLE_SKILLS[*]}"
        ;;
    "")
        # Install all skills
        echo -e "${BLUE}Installing all skills to $SKILLS_DST ...${NC}"
        echo ""

        mkdir -p "$SKILLS_DST"

        for skill in "${AVAILABLE_SKILLS[@]}"; do
            install_skill "$skill"
        done

        echo ""
        echo -e "${GREEN}══════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  All skills installed successfully!${NC}"
        echo -e "${GREEN}══════════════════════════════════════════════${NC}"
        echo ""
        echo -e "Skills are now available in Claude Code."
        echo -e "Restart Claude Code or start a new session to use them."
        echo ""
        echo -e "${YELLOW}Note:${NC} The ${YELLOW}github-kb${NC} skill defaults to ~/IdeaProjects."
        echo -e "Edit ${SKILLS_DST}/github-kb/SKILL.md to change the path."
        ;;
    *)
        # Install specific skill
        skill="$1"
        if [[ ! " ${AVAILABLE_SKILLS[*]} " =~ " $skill " ]]; then
            echo -e "${RED}Error: Unknown skill '$skill'${NC}"
            echo ""
            list_skills
            exit 1
        fi

        echo -e "${BLUE}Installing skill: $skill${NC}"
        echo ""
        mkdir -p "$SKILLS_DST"
        install_skill "$skill"
        echo ""
        echo -e "${GREEN}Done! Restart Claude Code to use the skill.${NC}"
        ;;
esac
