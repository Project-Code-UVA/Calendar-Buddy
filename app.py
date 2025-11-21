import os
import secrets
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = secrets.token_hex(32)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Global events list
events = []

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/upload", methods=["GET", "POST"])
def upload_page():
    global events
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'File uploaded: {filename}')

            # Example: auto-create event for demo
            events.append({
                "id": filename,
                "name": f"Event from {filename}",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "time": "12:00 PM",
                "location": "Online",
                "description": "Auto-generated event",
                "sourceFileName": filename
            })

            return redirect(url_for('upload_page'))

    uploaded_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        uploaded_files.append({
            "id": filename,
            "filename": filename
        })

    now = datetime.now()
    return render_template('upload.html', uploaded_files=uploaded_files, events=events, now=now)

@app.route("/delete/<file_id>")
def delete_file(file_id):
    global events
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_id))
        flash(f"{file_id} deleted")
        # Remove related events
        events = [e for e in events if e['sourceFileName'] != file_id]
    except FileNotFoundError:
        flash(f"{file_id} not found")
    return redirect(url_for('upload_page'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        abort(400, 'File not found')

if __name__ == "__main__":
    app.run(debug=True)
