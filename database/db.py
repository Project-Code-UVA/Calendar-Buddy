from datetime import datetime
from flask import current_app, g
import click
import sqlite3
import os

# database setup
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    schema_path = os.path.join("database", "schema.sql")

    with current_app.open_resource(schema_path) as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-db") # creates command line command called init-db that calls init_db
def init_db_command():
    # clear existing data and create new tables 
    init_db()
    click.echo("initialized the database")


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

# registers the functions with application
def init_app(app):
    app.teardown_appcontext(close_db) # flask will close_db after returning response
    app.cli.add_command(init_db_command) # adds a new command that can be called with the flask command
