from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)
SECRET_TOKEN = "my_super_secret_token"  # change this to something strong

@app.route("/cmd", methods=["POST"])
def run_cmd():
    token = request.headers.get("X-SECRET-TOKEN")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    data = request.json
    if not data or 'command' not in data:
        return jsonify({"error": "No command provided"}), 400

    command = data['command']
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

