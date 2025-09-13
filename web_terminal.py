import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace this with a strong secret token
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "supersecret")

@app.route("/")
def index():
    return "Web terminal is live! Use /run to execute commands."

@app.route("/run", methods=["POST"])
def run_command():
    token = request.headers.get("Authorization")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    data = request.json
    if not data or "command" not in data:
        return jsonify({"error": "No command provided"}), 400

    command = data["command"]
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns this automatically
    app.run(host="0.0.0.0", port=port)

