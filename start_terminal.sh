#!/bin/bash
# File: start_terminal.sh

# Activate Python virtual environment
source ~/A6_Cloud_Sandbox/venv/bin/activate

# Kill old session if exists
tmux kill-session -t a6_terminal 2>/dev/null

# Start Flask in a detached tmux session
tmux new-session -d -s a6_terminal "python ~/A6_Cloud_Sandbox/web_terminal.py"

echo "Flask web terminal is running inside tmux session 'a6_terminal'."
echo "Attach anytime with: tmux attach -t a6_terminal"

