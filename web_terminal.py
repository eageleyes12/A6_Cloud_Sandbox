#!/usr/bin/env python3
# web_terminal.py
# Simple Flask endpoint to run commands (AUTH REQUIRED via SECRET_TOKEN env var)
# WARNING: This runs shell commands on your machine/server. Keep SECRET_TOKEN secret.

import os
import subprocess
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Read secret token from environment (Render / system env)
SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

HTML_PAGE = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Web terminal</title></head>
<body>
  <h1>Web terminal is live!</h1>
  <p>Use <code>/run</code> to execute commands (POST JSON).</p>
  <form method="POST" action="/run">
    <input type="hidden" name="token" value="">
    <input type="text" name="command" style="width:80%" placeholder="command">
    <input type="submit" value="Run">
  </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE)

@app.route("/run", methods=["POST"])
def run_cmd():
    # Token: JSON body "token" field OR header "X-SECRET-TOKEN"
    token = None
    if request.is_json:
        token = request.json.get("token")
    if not token:
        token = request.headers.get("X-SECRET-TOKEN") or request.form.get("token")

    if not SECRET_TOKEN or token != SECRET_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    # command comes as JSON field "command" or form field "command"
    cmd = None
    if request.is_json:
        cmd = request.json.get("command")
    if not cmd:
        cmd = request.form.get("command")

    if not cmd:
        return jsonify({"error": "No command provided"}), 400

    # WARNING: shell=True executes arbitrary commands. Keep SECRET_TOKEN secret.
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render gives a PORT env var. Default to 5000 for local.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

