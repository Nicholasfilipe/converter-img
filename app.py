from flask import Flask, request, send_file, send_from_directory, render_template, url_for, redirect
from PIL import Image
import os
import zipfile
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
ZIP_PATH = 'converted_images.zip'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('images')
    converted_files = []

    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            with Image.open(filepath) as im:
                rgb_im = im.convert('RGB')
                new_filename = os.path.splitext(filename)[0] + '.jpeg'
                new_path = os.path.join(CONVERTED_FOLDER, new_filename)
                rgb_im.save(new_path, 'JPEG')
                converted_files.append(new_filename)
        except Exception as e:
            print(f"Erro ao converter {filename}: {e}")

    return render_template('download.html', files=converted_files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(CONVERTED_FOLDER, filename), as_attachment=True)

@app.route('/converted/<filename>')
def show_converted_image(filename):
    return send_from_directory(CONVERTED_FOLDER, filename)

@app.route('/download_all')
def download_all():
    with zipfile.ZipFile(ZIP_PATH, 'w') as zipf:
        for root, dirs, files in os.walk(CONVERTED_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)

    # Optionally delete all after zipping
    shutil.rmtree(UPLOAD_FOLDER)
    shutil.rmtree(CONVERTED_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CONVERTED_FOLDER, exist_ok=True)

    return send_file(ZIP_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
