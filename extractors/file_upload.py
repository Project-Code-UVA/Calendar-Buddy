import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    # returns True if file has . and ends in an allowed extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def home():
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
            flash('File successfully uploaded')
            return redirect(url_for('home')) # Redirect back to home after upload
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)