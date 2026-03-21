#!/bin/bash
# ============================================
# LAMBDA DEPLOY SCRIPT - Paste this entire block
# into your SSH session on the Lambda instance
# ============================================

echo "============================================"
echo "Setting up autoresearch on Lambda"
echo "============================================"

# Step 1: Clone the repo
cd ~
git clone https://github.com/bigbubs0/gqr-workspace.git
cd gqr-workspace/autoresearch

# Step 2: Install Python dependencies
pip install anthropic

# Step 3: Set your API key (REPLACE THIS WITH YOUR ACTUAL KEY)
# You can find it at https://console.anthropic.com/settings/keys
echo ""
echo "============================================"
echo "IMPORTANT: Set your Anthropic API key now"
echo "============================================"
echo ""
echo "Run this command (replace with your real key):"
echo ""
echo '  export ANTHROPIC_API_KEY="sk-ant-your-key-here"'
echo ""
echo "Then run this to start the loop:"
echo ""
echo '  cd ~/gqr-workspace/autoresearch && bash run-loop.sh'
echo ""
