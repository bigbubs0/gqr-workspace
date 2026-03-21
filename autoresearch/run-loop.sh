#!/bin/bash
# ============================================
# Run the autoresearch optimization loop
# ============================================

cd ~/gqr-workspace/autoresearch

# Verify API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    echo "Run: export ANTHROPIC_API_KEY=\"sk-ant-your-key-here\""
    exit 1
fi

echo "API key detected."

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code 2>/dev/null || {
        echo "npm not found, trying with apt..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        npm install -g @anthropic-ai/claude-code
    }
fi

echo "Claude Code ready."

# Run baseline eval first
echo ""
echo "============================================"
echo "Running baseline evaluation..."
echo "============================================"
python evals/runner.py prompts/current.md

echo ""
echo "============================================"
echo "Starting autoresearch loop..."
echo "============================================"
echo "This will run 20 cycles or until 90% pass rate."
echo "Monitor: tail -f results/optimization_log.md"
echo ""

# Launch the loop
claude --dangerously-skip-permissions \
  "Follow AGENT_INSTRUCTIONS.md and run the full optimization loop. Start by reading the file, then run the baseline eval, then begin optimization cycles."
