#!/bin/bash
# =============================================================================
# setup.sh — Lambda instance setup for rapid-source autoresearch
#
# Run once after cloning onto your Lambda instance:
#   bash setup.sh
#
# Prereqs (already on the instance):
#   - Python 3.8+
#   - Claude Code (claude CLI)
#   - ANTHROPIC_API_KEY exported in environment
# =============================================================================

set -e  # Exit on any error

echo "========================================================"
echo "  Rapid Source Autoresearch — Lambda Setup"
echo "========================================================"
echo ""

# ------------------------------------------------------------------
# 1. Verify Python version
# ------------------------------------------------------------------
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "Python version: $PYTHON_VERSION"
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✓ Python version OK"
else
    echo "ERROR: Python 3.8+ required"
    exit 1
fi

# ------------------------------------------------------------------
# 2. Install Python dependencies
# ------------------------------------------------------------------
echo ""
echo "Installing Python dependencies..."
pip install anthropic --quiet
echo "✓ anthropic installed"

# ------------------------------------------------------------------
# 3. Create directory structure (idempotent)
# ------------------------------------------------------------------
echo ""
echo "Creating directory structure..."
mkdir -p prompts/history
mkdir -p prompts/candidates
mkdir -p results
touch prompts/history/.gitkeep 2>/dev/null || true
touch prompts/candidates/.gitkeep 2>/dev/null || true
touch results/.gitkeep 2>/dev/null || true
echo "✓ Directories ready"

# ------------------------------------------------------------------
# 4. Verify the skill file exists
# ------------------------------------------------------------------
if [ ! -f "prompts/current.md" ]; then
    echo ""
    echo "ERROR: prompts/current.md not found."
    echo "This file should have been cloned with the repo."
    echo "If you see this error, check that the clone completed fully."
    exit 1
fi
echo "✓ Skill file found: prompts/current.md ($(wc -l < prompts/current.md) lines)"

# ------------------------------------------------------------------
# 5. Verify test cases
# ------------------------------------------------------------------
if [ ! -f "evals/test_cases.jsonl" ]; then
    echo ""
    echo "ERROR: evals/test_cases.jsonl not found."
    exit 1
fi
CASE_COUNT=$(grep -c '.' evals/test_cases.jsonl 2>/dev/null || echo 0)
echo "✓ Test cases found: $CASE_COUNT cases"

# ------------------------------------------------------------------
# 6. Check for Claude Code
# ------------------------------------------------------------------
echo ""
if command -v claude &> /dev/null; then
    echo "✓ Claude Code (claude CLI) found: $(which claude)"
else
    echo "WARNING: 'claude' CLI not found in PATH."
    echo "Install Claude Code before running the optimization loop:"
    echo "  https://docs.anthropic.com/en/docs/claude-code"
fi

# ------------------------------------------------------------------
# 7. Verify API key
# ------------------------------------------------------------------
echo ""
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is not set."
    echo ""
    echo "Set it with:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    echo "Then re-run this script:"
    echo "  bash setup.sh"
    exit 1
fi
echo "✓ ANTHROPIC_API_KEY is set (${#ANTHROPIC_API_KEY} chars)"

# ------------------------------------------------------------------
# 8. Run baseline evaluation
# ------------------------------------------------------------------
echo ""
echo "========================================================"
echo "  Running baseline evaluation (this takes 2-3 minutes)"
echo "========================================================"
echo ""
python3 evals/runner.py prompts/current.md
BASELINE_EXIT=$?

echo ""
echo "========================================================"
echo "  Setup Complete"
echo "========================================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "Option A — Full overnight optimization loop (recommended):"
echo "  claude --dangerously-skip-permissions \\"
echo "    'Follow AGENT_INSTRUCTIONS.md and run the full optimization loop'"
echo ""
echo "Option B — Single cycle (interactive):"
echo "  claude 'Read AGENT_INSTRUCTIONS.md. Run one optimization cycle.'"
echo ""
echo "Option C — Monitor progress in another terminal:"
echo "  tail -f results/optimization_log.md"
echo ""
echo "The optimized skill file will be at: prompts/current.md"
echo "Full run history: results/"
echo ""

# Exit 0 even if baseline eval "failed" (exit 1 = pass rate < 90%),
# because that's expected before optimization. Real errors will have
# already caused set -e to abort.
exit 0
