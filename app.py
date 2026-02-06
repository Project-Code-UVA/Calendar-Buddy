""" JAN 5, 2026 UPDATES """

""" 
llama3.2 implemented as ai parsing. 
to set up ollama -- (in your env)
- pip install -r requirements.txt
- install ollama on your computer
- run ollama: <ollama serve>
- <ollama run llama3.2> to download and run llama3.2

then extractors/ai.py should work but im not sure

CURRENT FUNCTIONALITIES
- ok at parsing formulaic / structured pdf documents. havent tested imgs. pretty slow
- /admin/cleanup page will clear your download/uploads folders and delete files saved in db
- /db will print current users and files saved in db
- legit .ics file generation (yay!)
"""

""" Note: running app.py will produce 'no page found error' because
flask automatically runs on http: but the google auth requires https.
Make sure to change to https://... (not http://) on the url, then reload."""

""" initialize the database using <flask --app app init-db> (sets up blank database)"""

import os
import json
import sqlite3

import secrets

# flask imports
from flask import (
    Flask, 
    render_template, 
    flash, 
    request, 
    redirect, 
    url_for, 
    send_from_directory, 
    send_file, 
    Response,
    abort,
    session)
from werkzeug.utils import secure_filename

# import extractors
from extractors.pdf_extractor import pdf_extractor
from extractors.image_extraction import image_extractor
from extractors.ai import event_extractor

# login imports
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from database.db import init_app, get_db

from ics_logic.generate_ics_file import generate_ics, ics_to_file

# google login configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "52505839374-j5o94mbmga0p284hqkm9p0a1kuuahjbq.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "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")
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg'}

# flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.secret_key = secrets.token_hex(32) # generates a 64-character hexadecimal string
app.config.from_mapping(
    DATABASE = os.path.join(app.instance_path, "database.db")
)
# database setup
init_app(app)

# user session setup
login_manager = LoginManager()
login_manager.init_app(app)
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    try:
        return requests.get(GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        print (f"Error: {e}")

class User(UserMixin):
    def __init__(self, id, name, email, profile_pic):
        self.id = id
        self.name = name
        self.email = email 
        self.profile_pic = profile_pic

    @staticmethod
    def get(id):
        db = get_db()
        user_row = db.execute(
            "SELECT * FROM user WHERE id = ?", (id,)
        ).fetchone()

        if user_row is None:
            return None
        
        return User(
            id=user_row["id"],
            name=user_row["name"],
            email=user_row["email"],
            profile_pic=user_row["profile_pic"],
        )
    
    @staticmethod
    def create(id, name, email, profile_pic):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) VALUES (?, ?, ?, ?)",
            (id, name, email, profile_pic)
        )
        db.commit()

    def __repr__(self):
        return f"User({self.name}, {self.email}, {self.profile_pic})"

# retrieve user from the db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def allowed_file(filename):
    # returns True if file has . and ends in an allowed extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        filename = request.args.get('filename')
        file_ready = request.args.get('file_ready') == "True"

        file_exists = False

        if filename and file_ready:
            if current_user.is_authenticated:
                file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
                file_exists = os.path.exists(file_path)
            else:
                file_exists = "event_details" in session

        return render_template(
            'index.html', 
            filename=filename if file_exists else None,
            file_ready=file_exists
            ) 

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
            filename = (secure_filename(file.filename)).lower() # secure the filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # save file to upload folder
            flash(f'File successfully uploaded. Filename: {filename}')
            
            # Process the uploaded file
            # get file path from upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 

            # extract text for PDF
            if filename.rsplit('.', 1)[1].lower() == 'pdf':
                text = None
                try:
                    text = pdf_extractor(file_path)
                except Exception as e:
                    print(f"error: {e}")

            elif filename.rsplit('.', 1)[1].lower() == 'txt':
                text = None
                try:
                    with open(file_path, 'r') as f:
                        text = f.read()
                except Exception as e:
                    print(f"error: {e}")
                    flash("could not read text file")
                
            else:
                flash('Text extraction unsuccessful. File type is not supported.')
                return redirect(request.url) 
            
            # parse text 
            if text:
                event_details = event_extractor(text) 
                flash(f'Extracted Event Details: {json.dumps(event_details, indent=4)}')
                
                # generate ics file 
                # save ics file to database
                if current_user.is_authenticated:
                    user_id = current_user.get_id()

                    new_filename = os.path.splitext(filename)[0] + "_" + user_id[:4] + ".ics"
                    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], new_filename)

                    # create calendar and write to file on disk
                    ics_str = generate_ics(event_details)
                    ics_to_file(download_path, ics_str)

                    try:
                        file_to_db(user_id, new_filename, file_path, download_path)
                    except Exception as e:
                        return f"Error: {e}"
                    
                    flash(f'{current_user.name} with ID {user_id} saved new file as: {new_filename}. Filepath: {download_path}')
                else: 
                    new_filename = os.path.splitext(filename)[0] + ".ics"
                    session["event_details"] = event_details

                    flash(f'Guest can download file as: {new_filename}')
                return redirect(url_for('home', filename=new_filename, file_ready=True)) # Redirect back to home after upload

    return render_template('index.html', filename=filename, file_ready=False)

@app.route("/home")
def home_page():
    return render_template("home.html")


def file_to_db(user_id, filename, old_name, file_path):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO files (user_id, filename, filepath, old_name) VALUES (?, ?, ?, ?)",
                       (user_id, filename, file_path, old_name))
        db.commit()
        flash("filepath added to database", "success")
    except sqlite3.Error as e:
        flash(f"database error: {e}", "error")

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    # logged in user -> file exists on disk
    if current_user.is_authenticated:
        downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
        print(f"Download path: {downloads}, filename: {filename}")
        try:
            return send_from_directory(downloads, 
                                       filename, 
                                       as_attachment=True, 
                                       mimetype="text/calendar"
                                       )
        except FileNotFoundError:
            abort(400, 'File not found')
    # guest -> regenerate file in memory
    else:
        event_details = session.get("event_details")

        if not event_details:
            abort(400, "No event data available")
        
        ics_str = generate_ics(event_details)

        return Response(
            ics_str,
            mimetype="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

@app.route("/login")
def login():
    # get URL for google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # use the library to construct the request for google login
    # allow retrieval of user profile from google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

# retrieve authorization code from google
@app.route("/login/callback")
def callback():
    # get authorization code google sent back to us
    code = request.args.get("code")
    # find out what url to get tokens (which allow us to get things on behalf of the user) from 
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code)
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # parse tehe tokens
    client.parse_request_body_response(token_response.text) #json.dumps(token_response.json())

    # use tokens now to hit the url that gives the user profile info
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # parse response from userinfo_endpoint
    # check that email is verified 
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]     # sub = subject, a unique identifier for the user
        users_email = userinfo_response.json()["email"] # email = user's google email
        picture = userinfo_response.json()["picture"]   # picture = user's pfp on google
        users_name = userinfo_response.json()["given_name"] # given_name = user's first and last name 
    else:
        return "User email not available or not verified by Google"

    # create user in the db with this info
    user = User(
        id=unique_id, 
        name=users_name, 
        email=users_email, 
        profile_pic=picture
    )
    # if user doesnt exist, add it to the db
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)
    # begin user session by logging the user in
    login_user(user)

    # send user back to homepage 
    return redirect(url_for("home"))


@app.route("/logout")
@login_required # from flask-login and ensures only logged in users can access thsi endpoint
def logout():
    logout_user()
    return redirect(url_for("home"))

# for debugging: check all users in database
@app.route("/db")
def list_users_and_files():
    db = get_db()
    users = db.execute("SELECT * FROM user").fetchall() # fetchall returns a list of sqlite3.Row objects
    print("---All Users in Database---")
    for user in users:
        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    print("---End---")

    files = db.execute("SELECT * FROM files").fetchall() # fetchall returns a list of sqlite3.Row objects
    print("---All files in Database---")
    for file in files:
        print(f"ID: {file['id']}, User_ID: {file['user_id']}, filename: {file['filename']}, filepath: {file['filepath']}, old filepath: {file['old_name']}")
    print("---End---")

    return "users and files printed in terminal"

# clean up db and disk folders
@app.route("/admin/cleanup")
def cleanup_db():
    db = get_db()

    UPLOAD_DIR = os.path.join(app.root_path, "uploads")
    DOWNLOAD_DIR = os.path.join(app.root_path, "downloads")

    rows = db.execute(
        "SELECT filepath, old_name FROM files"
    ).fetchall()

    results = []

    for filepath, old_file in rows:
        for file, base_dir, label in [
            (filepath, DOWNLOAD_DIR, "downloads"),
            (old_file, UPLOAD_DIR, "uploads"),
        ]:
            if not file:
                continue

            abs_path = os.path.abspath(
                os.path.join(app.root_path, file)
            )

            # security check
            if os.path.commonpath([abs_path, base_dir]) != base_dir:
                results.append({
                    "file": file,
                    "folder": label,
                    "status": "Skipped (unsafe path)"
                })
                continue

            if os.path.exists(abs_path):
                try:
                    os.remove(abs_path)
                    results.append({
                        "file": file,
                        "folder": label,
                        "status": "Deleted"
                    })
                except Exception as e:
                    results.append({
                        "file": file,
                        "folder": label,
                        "status": f"Error: {e}"
                    })
            else:
                results.append({
                    "file": file,
                    "folder": label,
                    "status": "File not found"
                })

    db.execute("DELETE FROM files")
    db.commit()

    # PURGE UPLOAD FOLDER of guest files (not saved in db)
    if os.path.isdir(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            abs_path = os.path.join(UPLOAD_DIR, filename)

            # only delete files, never directories
            if not os.path.isfile(abs_path):
                continue
            if filename == ".gitkeep":
                continue

            try:
                os.remove(abs_path)
                results.append({
                    "file": f"uploads/{filename}",
                    "status": "Deleted (guest upload)"
                })
            except Exception as e:
                results.append({
                    "file": f"uploads/{filename}",
                    "status": f"Error: {e}"
                })

    return render_template("admin.html", cleanup_results=results)


if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")