from flask import Flask, render_template, request, send_from_directory
import os
import datetime
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def calculate_hash(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(4096)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def save_file_with_hash(file):
    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    file_hash = calculate_hash(filepath)
    with open('hashes.txt', 'a') as f:
        f.write(f"{filename}: {file_hash}\n")
    return filename, file_hash

@app.template_filter('datetime')
def format_datetime(value):
    return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename, file_hash = save_file_with_hash(file)
            return f'File uploaded successfully. Hash: {file_hash}'
    
    files = os.listdir(UPLOAD_FOLDER)
    # Group by extension
    files_by_extension = {}
    for file in files:
        extension = file.split('.')[-1]
        files_by_extension.setdefault(extension, []).append(file)

    return render_template('index.html', files_by_extension=files_by_extension)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open('hashes.txt', 'r') as f:
        for line in f:
            if filename in line:
                stored_hash = line.split(': ')[1].strip()
                break
        else:
            return "Hash for this file not found", 404

    current_hash = calculate_hash(filepath)
    if stored_hash != current_hash:
        return "File has been tampered with!", 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/files', methods=['GET'])
# def list_files():
#     files = os.listdir(app.config['UPLOAD_FOLDER'])
#     file_info = []
#     for file in files:
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
#         file_info.append({
#             'filename': file,
#             'hash': calculate_file_hash(file_path)
#         })
#     return jsonify({'files': file_info}), 200

# @app.route('/sync', methods=['POST'])
# def sync_files():
#     try:
#         sync_url = request.json.get('url')
#         if not sync_url:
#             return jsonify({'error': 'No sync URL provided'}), 400


#             # Zrób download jeżeli plik nie istnieje w przestrzeni lokalnej lub hash jest naruszony
#             if not os.path.exists(local_file_path) or calculate_file_hash(local_file_path) != remote_file['hash']:
#                 download_response = requests.get(f"{sync_url}/download/{remote_file['filename']}", stream=True)
#                 if download_response.status_code == 200:
#                     with open(local_file_path, 'wb') as f:
#                         for chunk in download_response.iter_content(chunk_size=8192):
#                             f.write(chunk)
#                 else:
#                     return jsonify({'error': f"Failed to download file {remote_file['filename']} from remote server"}), download_response.status_code

#         return jsonify({'message': 'Files synchronized successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)