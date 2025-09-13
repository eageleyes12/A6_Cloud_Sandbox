# Overwrite web_terminal.py with the recommended code
cat > ~/A6_Cloud_Sandbox/web_terminal.py <<'PY'
#!/usr/bin/env python3
import os
import shlex
import subprocess
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Read secret token from environment (do NOT hardcode)
SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

HTML_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Web Command Executor</title>
</head>
<body>
  <h2>Web Command Executor</h2>
  <p><strong>Warning:</strong> this page sends commands to be executed on the server. Keep your token secret.</p>

  <label>Secret token:</label><br>
  <input id="token" style="width: 50%;" placeholder="Enter SECRET_TOKEN"><br><br>

  <label>Command:</label><br>
  <input id="command" style="width: 80%;" placeholder="ls -la /"><button id="run">Run</button>

  <h3>Result</h3>
  <pre id="output" style="white-space: pre-wrap; border: 1px solid #ccc; padding: 10px; min-height: 120px;"></pre>

  <script>
    document.getElementById('run').addEventListener('click', async () => {
      const token = document.getElementById('token').value.trim();
      const command = document.getElementById('command').value.trim();
      if (!token || !command) {
        alert('Please enter both token and command.');
        return;
      }
      document.getElementById('output').textContent = 'Running...';
      try {
        const res = await fetch('/run', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token, command })
        });
        const data = await res.json();
        document.getElementById('output').textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        document.getElementById('output').textContent = 'Error: ' + err;
      }
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/run", methods=["POST"])
def run_command():
    # Ensure SECRET_TOKEN is configured
    if not SECRET_TOKEN:
        return jsonify({"error": "Server misconfigured: SECRET_TOKEN not set"}), 500

    data = request.get_json(force=True, silent=True)
    if not data or "token" not in data or "command" not in data:
        return jsonify({"error": "Invalid request: require JSON with 'token' and 'command'"}), 400

    if data["token"] != SECRET_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    command = data["command"]
    # WARNING: running shell=True will run arbitrary commands. Keep token private.
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
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
    # Render provides PORT env var; otherwise default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 for Render / external access
    app.run(host="0.0.0.0", port=port)
PY

