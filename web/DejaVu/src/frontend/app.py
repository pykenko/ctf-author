from flask import Flask, request, render_template_string, jsonify
import os
import requests
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)

SHARED_DIR = '/challenge_tmp'
ALLOWED_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tif', '.tiff', '.svg',
    '.djvu', '.djv'
}

UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
        .card { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 640px; margin: 0 auto; }
        .nav { margin-top: 18px; text-align: center; }
        .nav a { color: #2196f3; text-decoration: none; margin: 0 10px; font-weight: bold; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>File Processor</h1>
        <p>Upload an image for metadata processing.</p>

        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*,.djvu,.djv">
            <input type="submit" value="Upload & Process">
        </form>

        <div class="nav">
            <a href="/documentation">Documentation</a>
            <a href="/bulb">Bulb</a>
        </div>
    </div>
</body>
</html>
"""

DOCUMENTATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
        .card { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 720px; margin: 0 auto; line-height: 1.6; }
        .note { background: #eaeaea; padding: 14px; border-radius: 4px; margin: 16px 0; }
        a { color: #2196f3; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Documentation</h1>
        <p>The bulb status reflects the existence of the file: <code>/challenge_tmp/ping.txt</code></p>
        <p>The flag is stored at : <code>/flag.txt</code></p>
        <div class="note">
            We use older versions of linux metadata checkers to lower cost and keep the processing pipeline efficient.
            That means some legacy parsing behavior is still present in the stack.
        </div>
        <p><a href="/">Back to upload</a> | <a href="/bulb">Open bulb</a></p>
    </div>
</body>
</html>
"""

BULB_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bulb Oracle</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
        .card { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 640px; margin: 0 auto; }
        .bulb { width: 60px; height: 60px; border-radius: 50%; display: block; margin: 20px auto; border: 3px solid #333; }
        .off { background-color: #555; box-shadow: inset 0 0 10px #000; }
        .on { background-color: #ffeb3b; box-shadow: 0 0 20px #ffeb3b, inset 0 0 5px #fff; }
        .info-text { background-color: #eaeaea; padding: 12px; border-radius: 4px; margin-bottom: 20px; text-align: center; font-size: 0.95em; }
        button { padding: 10px 15px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn-check { background-color: #4caf50; color: white; }
        .btn-sim { background-color: #2196f3; color: white; }
        .btn-reset { background-color: #f44336; color: white; }
        .center { text-align: center; }
        .nav { margin-top: 18px; text-align: center; }
        .nav a { color: #2196f3; text-decoration: none; margin: 0 10px; font-weight: bold; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Bulb Oracle</h1>
        <div class="info-text">
            The bulb status reflects the existence of the file: <code>/challenge_tmp/ping.txt</code>
        </div>

        <h3 class="center">Oracle Status (The Bulb)</h3>
        <div id="bulb" class="bulb off"></div>
        
        <div class="center">
            <button class="btn-check" onclick="checkBulb()">Check Status</button>
            <button class="btn-sim" onclick="simulatePing()">Create Ping File</button>
            <button class="btn-reset" onclick="resetBulb()">Delete Ping File</button>
        </div>

        <div class="nav">
            <a href="/">Upload</a>
            <a href="/documentation">Documentation</a>
        </div>
    </div>

    <script>
        async function checkBulb() {
            let res = await fetch('/check');
            let data = await res.json();
            document.getElementById('bulb').className = data.status ? "bulb on" : "bulb off";
        }
        async function simulatePing() {
            await fetch('/simulate', {method: 'POST'});
            checkBulb();
        }
        async function resetBulb() {
            await fetch('/reset', {method: 'POST'});
            document.getElementById('bulb').className = "bulb off";
        }
        checkBulb();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UPLOAD_TEMPLATE)


@app.route('/documentation')
def documentation():
    return render_template_string(DOCUMENTATION_TEMPLATE)


@app.route('/bulb')
def bulb():
    return render_template_string(BULB_TEMPLATE)


def allowed_image(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_IMAGE_EXTENSIONS


def forward_to_backend(filename, file_content, mime_type):
    try:
        files = {'file': (filename, file_content, mime_type)}
        requests.post("http://backend:5001/process", files=files, timeout=6)
    except Exception:
        pass


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if not allowed_image(file.filename):
        return "Only image uploads are accepted.", 400
    
    file_content = file.read()
    safe_name = secure_filename(file.filename)
    if safe_name.lower().endswith(('.djvu', '.djv')):
        mime_type = 'image/vnd.djvu'
    else:
        mime_type = file.mimetype or 'application/octet-stream'

    threading.Thread(
        target=forward_to_backend,
        args=(safe_name, file_content, mime_type),
        daemon=True,
    ).start()

    return "File uploaded. Processing complete."

@app.route('/check', methods=['GET'])
def check_status():
    exists = os.path.exists(os.path.join(SHARED_DIR, 'ping.txt'))
    return jsonify({"status": exists})

@app.route('/simulate', methods=['POST'])
def simulate_status():
    target_file = os.path.join(SHARED_DIR, 'ping.txt')
    with open(target_file, 'w') as f:
        f.write('ping')
    return jsonify({"success": True})

@app.route('/reset', methods=['POST'])
def reset_status():
    target_file = os.path.join(SHARED_DIR, 'ping.txt')
    if os.path.exists(target_file):
        os.remove(target_file)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
