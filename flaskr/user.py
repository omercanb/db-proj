from werkzeug.security import generate_password_hash

from flaskr.db import get_db


def create_user(username, password):
    db = get_db()
    cursor = db.execute(
        "insert into User (username, password) values (?, ?)",
        (username, generate_password_hash(password)),
    )
    return cursor.lastrowid  # returns the new id


def create_branch(username, name, password):
    db = get_db()
    cursor = db.execute(
        "insert into Branch (username, name, password) values (?, ?, ?)",
        (username, name, generate_password_hash(password)),
    )
    return cursor.lastrowid  # returns the new id
