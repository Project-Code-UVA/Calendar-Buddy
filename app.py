# Imports
from flask import Flask

# Initialize Flask app
app = Flask(__name__)


# Home page
@app.route("/")
def index():
    return "HOME"


if __name__ == "__main__":
    app.run(debug=True)
