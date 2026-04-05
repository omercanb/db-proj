import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.user import create_user, get_user, get_user_by_id

bp = Blueprint("stores", __name__, url_prefix="/stores")


@bp.route("/")
def stores():
    db = get_db()

    search = request.args.get("search", "")

    stores = db.execute(
        "select * from Store where name like ?", (f"%{search}%",)
    ).fetchall()

    # stores = db.execute("select * from Store").fetchall()

    return render_template("stores/stores.html", stores=stores, search=search)


def create_store(username, name, password, ignore=False):
    db = get_db()
    cursor = db.execute(
        f"insert {'' if not ignore else 'or ignore'} into Store (username, name, password) values (?, ?, ?)",
        (username, name, generate_password_hash(password)),
    )
    db.commit()
    return cursor.lastrowid  # returns the new id


def get_store(username):
    return (
        get_db()
        .execute("SELECT * FROM store WHERE username = ?", (username,))
        .fetchone()
    )


def get_store_by_id(store_id):
    return get_db().execute("SELECT * FROM store WHERE id = ?", (store_id,)).fetchone()


def seed_stores():
    stores = [
        ("mcdonalds", "Big Boy Playhouse", "pass"),
        ("moderator", "The Dawg Pen", "pass"),
        ("westside_lodge", "The Den", "pass"),
    ]

    for username, name, password in stores:
        create_store(username, name, password, ignore=True)
