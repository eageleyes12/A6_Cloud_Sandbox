#!/usr/bin/env python3
import os
import subprocess
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Read secret token from environment
SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

# Simple web UI (optional)
HTML_PAGE = """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Web Terminal</title></head>
  <body>
    <h1>Web terminal is live!</h1>
    <p>Use <code>/run</code> POST with JSON <code>{"token":"...","command":"..."}</code></p>
    <form id="f" method="post" action="/run" style="margin-top:1em">
      <label>Token: <input name="token" style="width:80%"></label><br><br>
      <label>Command: <input name="command" style="width:80%" value="ls -la"></label><br><br>
      <button type="submit">Run</button>
    </form>
    <pre id="out"></pre>
    <script>
      const form = document.getElementById('f');
      const out = document.getElementById('out');
      form.onsubmit = async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        const body = { token: fd.get('token'), command: fd.get('command') };
        const res = await fetch('/run', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body)
        });
        out.textContent = await res.text();
      };
    </script>
  </body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE)

@app.route("/run", methods=["POST"])
def run_command():
    # Accept JSON; also handle form submit from UI by converting form-like payloads
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        # form POST from the simple UI
        data = {
            "token": request.form.get("token"),
            "command": request.form.get("command")
        }

    if not data:
        return jsonify({"error": "Invalid request (no JSON or form data)"}), 400

    token = data.get("token")
    if SECRET_TOKEN is None:
        return jsonify({"error": "Server misconfigured: SECRET_TOKEN not set"}), 500

    if token != SECRET_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    command = data.get("command")
    if not command:
        return jsonify({"error": "No command provided"}), 400

    # WARNING: This runs arbitrary shell commands. Keep SECRET_TOKEN secret.
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=60
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
    # Render provides PORT in environment; fallback to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 for external access
    app.run(host="0.0.0.0", port=port)

