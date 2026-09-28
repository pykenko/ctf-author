from flask import Flask, request
import subprocess
import os
import sys
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

SHARED_DIR = '/challenge_tmp'
ALLOWED_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tif', '.tiff', '.svg',
    '.djvu', '.djv'
}


def allowed_image(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_IMAGE_EXTENSIONS


def is_valid_image_file(path, filename):
    if not allowed_image(filename):
        return False

    _, ext = os.path.splitext(filename.lower())

    with open(path, 'rb') as handle:
        header = handle.read(16)

    if header.startswith(b'\xff\xd8\xff'):
        return True
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return True
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        return True
    if header.startswith(b'BM'):
        return True
    if header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):
        return True
    if header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WEBP':
        return True
    if ext in {'.svg'}:
        return header.lstrip().startswith((b'<?xml', b'<svg', b'<!doctype svg'))
    if header.startswith(b'AT&TFORM'):
        return True

    return False

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return "No file provided", 400
        
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    safe_name = secure_filename(file.filename)
    _, ext = os.path.splitext(safe_name)
    if not ext:
        ext = '.img'
    upload_path = os.path.join(SHARED_DIR, f"{uuid.uuid4().hex}{ext.lower()}")

    file.save(upload_path)

    if not is_valid_image_file(upload_path, safe_name):
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return "Only image uploads are accepted.", 400

    print(f"Received image file saved to {upload_path}", file=sys.stderr)

    try:
        result = subprocess.run(
            ['exiftool', upload_path],
            capture_output=True, 
            text=True, 
            timeout=5
        )

        if os.path.exists(upload_path):
            os.remove(upload_path)

        if result.returncode != 0:
            return "Metadata extraction failed.", 500

        return "File processed successfully."

    except Exception as e:
        print(f"Critical Engine Error: {str(e)}", file=sys.stderr)
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return "Engine processing error.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
