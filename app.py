import os
import secrets
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from pdf_extractor import extract_text_from_pdf
from nlp_extraction import nlp_extractor
from image_extraction import image_extractor

UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.secret_key = secrets.token_hex(32) # generates a 64-character hexadecimal string

def allowed_file(filename):
    # returns True if file has . and ends in an allowed extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def home():
    filename = request.args.get('filename')
    file_exists = False
    if filename:
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        file_exists = os.path.exists(file_path)

    return render_template('index.html', filename=filename if file_exists else None)

@app.route("/", methods=["POST"])
def uploads():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files: # request.files is a dictionary-like object containing uploaded files
            flash('No file part') # use get_flashed_messages() in template to display
            return redirect(request.url) # redirect to the upload page
        file = request.files['file'] # access an uploaded file in flask
        # if user does not select a file, the browser submits an
        # empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # secure the filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # save file to upload folder
            flash(f'File successfully uploaded. Filename: {filename}')

            # Process the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if filename.rsplit('.', 1)[1].lower() == 'pdf':
                text = extract_text_from_pdf(file_path)
                new_filename = filename.removesuffix('.pdf') + '.txt'
                download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], new_filename)
                with open(download_path, "w") as f:
                    f.write(text)
                
                event_details = nlp_extractor(text)
                flash(f'Extracted Event Details: {event_details}')
                flash(f'New file saved as: {new_filename}')

                return redirect(url_for('home', filename=new_filename)) # Redirect back to home after upload

            else:
                flash('Only PDFs are supported right now')
                return redirect(request.url)
        
    return render_template('index.html', filename=filename)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    print(f"Download path: {downloads}, filename: {filename}")
    try:
        return send_from_directory(downloads, filename, as_attachment=True)
    except FileNotFoundError:
        abort(400, 'File not found')

if __name__ == "__main__":
    app.run(debug=True)