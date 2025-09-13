#!/bin/bash

# Activate Python virtual environment
source ~/A6_Cloud_Sandbox/venv/bin/activate

# Kill old tmux session if it exists
tmux kill-session -t a6_terminal 2>/dev/null

# Start Flask web terminal in a detached tmux session
tmux new-session -d -s a6_terminal "python ~/A6_Cloud_Sandbox/web_terminal.py"

# Kill old ngrok process if it exists
pkill ngrok 2>/dev/null

# Start ngrok tunnel in background
ngrok http 5000 --log=stdout > ~/A6_Cloud_Sandbox/ngrok.log 2>&1 &

# Wait for ngrok to initialize and produce a public URL
NGROK_URL=""
RETRIES=15  # number of attempts
SLEEP_INTERVAL=1

for i in $(seq 1 $RETRIES); do
    sleep $SLEEP_INTERVAL
    NGROK_JSON=$(curl --silent http://127.0.0.1:4040/api/tunnels 2>/dev/null)
    if [ -n "$NGROK_JSON" ] && echo "$NGROK_JSON" | grep -q "public_url"; then
        NGROK_URL=$(echo "$NGROK_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])")
        break
    fi
done

# Save the link if successful
if [ -n "$NGROK_URL" ]; then
    echo $NGROK_URL > ~/A6_Cloud_Sandbox/current_link.txt
    echo "Flask web terminal is running in tmux session 'a6_terminal'."
    echo "Current ngrok link saved to ~/A6_Cloud_Sandbox/current_link.txt: $NGROK_URL"
else
    echo "Error: Could not retrieve ngrok public URL after $RETRIES attempts."
fi

