#!/bin/bash
# Bootstrap Bryan Blair's GQR Recruiting Workspace
# Usage: ./bootstrap.sh [workspace_dir]
#
# Sets up Claude Code environment by symlinking skills,
# copying memory files, and configuring MCP.
#
# Run this after cloning the repo to a new machine.

set -euo pipefail

WORKSPACE_DIR="${1:-$(pwd)}"
CLAUDE_DIR="$HOME/.claude"

echo "=== GQR Workspace Bootstrap ==="
echo "Workspace: $WORKSPACE_DIR"
echo "Claude dir: $CLAUDE_DIR"
echo ""

# Verify we're in the right repo
if [ ! -f "$WORKSPACE_DIR/CLAUDE.md" ]; then
    echo "ERROR: CLAUDE.md not found in $WORKSPACE_DIR"
    echo "Run this from the cloned gqr-workspace repo root."
    exit 1
fi

# 1. Create Claude directories
echo "[1/6] Creating Claude Code directories..."
mkdir -p "$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR/scheduled-tasks"
mkdir -p "$CLAUDE_DIR/projects"

# 2. Install global CLAUDE.md
echo "[2/6] Installing global CLAUDE.md..."
if [ -f "$WORKSPACE_DIR/.claude/CLAUDE.md.global" ]; then
    cp "$WORKSPACE_DIR/.claude/CLAUDE.md.global" "$CLAUDE_DIR/CLAUDE.md"
    echo "  Copied to $CLAUDE_DIR/CLAUDE.md"
else
    echo "  WARNING: .claude/CLAUDE.md.global not found, skipping"
fi

# 3. Symlink skills
echo "[3/6] Symlinking skills..."
SKILLS_DIR="$WORKSPACE_DIR/skills"
if [ -d "$SKILLS_DIR" ]; then
    for skill_file in "$SKILLS_DIR"/*.md; do
        skill_name=$(basename "$skill_file" .md)
        target_dir="$CLAUDE_DIR/skills/$skill_name"
        mkdir -p "$target_dir"
        # Create symlink or copy (Windows doesn't always support symlinks)
        if ln -sf "$skill_file" "$target_dir/SKILL.md" 2>/dev/null; then
            echo "  Linked: $skill_name"
        else
            cp "$skill_file" "$target_dir/SKILL.md"
            echo "  Copied: $skill_name (symlink failed)"
        fi
    done
else
    echo "  WARNING: skills/ directory not found"
fi

# 4. Copy scheduled tasks
echo "[4/6] Copying scheduled tasks..."
if [ -d "$WORKSPACE_DIR/.claude/scheduled-tasks" ]; then
    cp -r "$WORKSPACE_DIR/.claude/scheduled-tasks/"* "$CLAUDE_DIR/scheduled-tasks/" 2>/dev/null || true
    echo "  Copied scheduled tasks to $CLAUDE_DIR/scheduled-tasks/"
else
    echo "  WARNING: .claude/scheduled-tasks/ not found"
fi

# 5. Copy memory files
echo "[5/6] Restoring memory files..."
MEMORY_SRC="$WORKSPACE_DIR/.claude/memory-backup"
if [ -d "$MEMORY_SRC" ]; then
    # Claude Code uses a hash of the workspace path for memory storage
    # We'll copy to a known location and let the user move it
    MEMORY_DEST="$WORKSPACE_DIR/.claude/memory-restore"
    mkdir -p "$MEMORY_DEST"
    cp "$MEMORY_SRC/"* "$MEMORY_DEST/" 2>/dev/null || true
    echo "  Memory files staged at .claude/memory-restore/"
    echo "  NOTE: Copy these to your Claude Code project memory directory after first run."
else
    echo "  WARNING: .claude/memory-backup/ not found"
fi

# 6. Check Python dependencies
echo "[6/6] Checking Python dependencies..."
if command -v python3 &>/dev/null || command -v python &>/dev/null; then
    PY=$(command -v python3 2>/dev/null || command -v python)
    echo "  Python found: $($PY --version 2>&1)"

    if [ -f "$WORKSPACE_DIR/recruiter-tool/requirements.txt" ]; then
        echo "  To install recruiter-tool deps: pip install -r recruiter-tool/requirements.txt"
    fi
else
    echo "  WARNING: Python not found. Install Python 3.10+ for full functionality."
fi

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Next steps:"
echo "  1. Open this workspace in Claude Code: cd $WORKSPACE_DIR && claude"
echo "  2. Rotate your OpenAI API key (old one was in git history)"
echo "  3. Set up .env files for any tools that need API keys"
echo "  4. Re-authenticate Notion MCP plugin if needed"
echo ""
echo "Key files:"
echo "  CLAUDE.md          - Main operating context"
echo "  skills/            - All recruiting skills"
echo "  config/            - Notion DB IDs, Make scenarios"
echo "  Knowledge Base/    - Reference docs (PDFs may need re-download)"
echo "  Documents/         - Obsidian vault, context profiles"
