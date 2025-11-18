""" Note: running app.py will produce 'no page found error' because
flask automatically runs on http: but the google auth requires https.
Make sure to change to https://... (not http://) on the url, then reload."""


import os
import json
import sqlite3

import secrets
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from extractors.pdf_extractor import pdf_extractor
from extractors.nlp_extraction import nlp_extractor
from extractors.image_extraction import image_extractor
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
try:
    init_app(app)
except sqlite3.OperationalError:
    pass
""" run the init-db command using <flask --app app init-db> """

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
                text = pdf_extractor(file_path)
                new_filename = filename.removesuffix('.pdf') + '.txt'
                download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], new_filename)
                with open(download_path, "w") as f:
                    f.write(text)
                event_details = nlp_extractor(text)
                flash(f'Extracted Event Details: {event_details}')
                flash(f'New file saved as: {new_filename}')

                return redirect(url_for('home', filename=new_filename)) # Redirect back to home after upload
            elif filename.rsplit('.', 1)[1].lower() in ["png", "jpg", "jpeg"]:
                text = image_extractor(file_path)
                print (text)
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
@app.route("/users")
def list_users():
    db = get_db()
    users = db.execute("SELECT * FROM user").fetchall() # fetchall returns a list of sqlite3.Row objects
    print("---All Users in Database---")
    for user in users:
        print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")

    return "Users printed in terminal"

if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")