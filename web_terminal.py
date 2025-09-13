
from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# Basic HTML page with a command input
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>A6 Cloud Terminal</title>
</head>
<body>
    <h1>A6 Cloud Terminal</h1>
    <form method="POST">
        <input type="text" name="cmd" style="width: 80%;" autofocus>
        <input type="submit" value="Run">
    </form>
    {% if output %}
    <h2>Output:</h2>
    <pre>{{ output }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    if request.method == "POST":
        cmd = request.form.get("cmd")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)
    return render_template_string(HTML_PAGE, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

