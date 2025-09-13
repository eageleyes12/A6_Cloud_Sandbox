#!/bin/bash
source ~/A6_Cloud_Sandbox/venv/bin/activate

while true; do
    python ~/A6_Cloud_Sandbox/web_terminal.py
    echo "A6 crashed at $(date). Restarting in 2 seconds..."
    sleep 2
done

