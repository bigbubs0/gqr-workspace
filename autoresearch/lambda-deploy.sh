#!/bin/bash
# ============================================
# LAMBDA DEPLOY - Paste into your SSH session
# Uses Claude Max subscription, no API key needed
# ============================================

echo "============================================"
echo "Setting up autoresearch on Lambda"
echo "============================================"

# Step 1: Clone the repo
cd ~
git clone https://github.com/bigbubs0/gqr-workspace.git
cd gqr-workspace/autoresearch

# Step 2: Install Claude Code if needed
if ! command -v claude &> /dev/null; then
    echo "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code 2>/dev/null || {
        echo "Installing Node.js first..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        npm install -g @anthropic-ai/claude-code
    }
fi

echo ""
echo "============================================"
echo "Setup complete."
echo "============================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Log into Claude Code (one time):"
echo "     claude login"
echo ""
echo "  2. Start the optimization loop:"
echo "     cd ~/gqr-workspace/autoresearch && bash run-loop.sh"
echo ""
