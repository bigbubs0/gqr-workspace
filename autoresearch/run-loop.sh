#!/bin/bash
# ============================================
# Run the autoresearch optimization loop
# Uses Claude Max subscription via Claude Code CLI
# No API key needed
# ============================================

cd ~/gqr-workspace/autoresearch

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code 2>/dev/null || {
        echo "npm not found, installing Node.js first..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        npm install -g @anthropic-ai/claude-code
    }
fi

# Check if logged in
echo "Checking Claude Code login..."
claude --version
echo ""
echo "If you're not logged in yet, run: claude login"
echo ""

# Run baseline eval first
echo "============================================"
echo "Running baseline evaluation..."
echo "============================================"
python evals/runner.py prompts/current.md

echo ""
echo "============================================"
echo "Starting autoresearch loop..."
echo "============================================"
echo "This will run up to 20 cycles or until 90% pass rate."
echo "Monitor: tail -f results/optimization_log.md"
echo ""

# Launch the loop
claude --dangerously-skip-permissions \
  "Follow AGENT_INSTRUCTIONS.md and run the full optimization loop. Start by reading the file, then run the baseline eval, then begin optimization cycles."
