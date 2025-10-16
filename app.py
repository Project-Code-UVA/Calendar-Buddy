# Imports
from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)


# Home page
@app.route("/")
def index():
    return "HOME"
    #render_template("index.html") # Render the index.html template as home page


if __name__ == "__main__":
    app.run(debug=True)
