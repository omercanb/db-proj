import functools
import random
from datetime import date

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
from werkzeug.security import generate_password_hash

from flaskr import game
from flaskr.db import get_db
from flaskr.game import (
    create_game,
    create_game_copy,
    get_available_games,
    get_available_games_with_counts,
    get_game_copies,
    get_unavailable_games,
)
from flaskr.session import create_session, get_available_tables, get_unavailable_tables
from flaskr.user import create_user

bp = Blueprint("stores", __name__)


@bp.before_app_request
def load_logged_in_store():
    store_id = session.get("store_id")

    if store_id is None:
        g.store = None
    else:
        g.store = get_store_by_id(store_id)


def store_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.store is None:
            return redirect(url_for("auth.loginstore"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/")
def stores():
    db = get_db()

    search = request.args.get("search", "")

    stores = db.execute(
        "select * from Store where name like ?", (f"%{search}%",)
    ).fetchall()

    # stores = db.execute("select * from Store").fetchall()

    return render_template("stores/stores.html", stores=stores, search=search)


@bp.route("/mystore")
@store_login_required
def my_store():
    tables = get_tables(g.store["id"])
    print(tables)
    game_copies = get_game_copies(g.store["id"])
    return render_template(
        "stores/my_store.html", tables=tables, game_copies=game_copies
    )


@bp.route("/store/<int:store_id>")
def store(store_id):
    store = get_store_by_id(store_id)
    tables = get_tables(store_id)
    games = get_available_games_with_counts(store_id)
    return render_template("stores/store.html", store=store, tables=tables, games=games)
    # else:
    #     # A request is made for the available tables
    #     tables = get_available_tables(store_id, start_time, end_time)
    #     print(tables)
    #     game_copies = get_game_copies(store_id)
    #     return render_template(
    #         "stores/store.html",
    #         tables=tables,
    #         game_copies=game_copies,
    #         start_time=start_time,
    #         end_time=end_time,
    #     )


@bp.route("/store/<int:store_id>/book")
def book_session(store_id):
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    day = request.args.get("day")
    if not start_time:
        start_time = 9
        end_time = 20
        day = str(date.today())
    tables = get_available_tables(store_id, day, start_time, end_time)
    unvailable_tables = get_unavailable_tables(store_id, day, start_time, end_time)
    store = get_store_by_id(store_id)
    return render_template(
        "stores/book_session.html",
        store=store,
        tables=tables,
        unvailable_tables=unvailable_tables,
        day=day,
        today=str(date.today()),
        start_time=start_time,
        end_time=end_time,
    )


@bp.route("/store/<int:store_id>/table/<int:table_num>/select-games")
def select_games(store_id, table_num):
    if not g.user:
        return redirect(url_for("auth.login"))

    start_time = request.args.get("start_time", 9, type=int)
    end_time = request.args.get("end_time", 20, type=int)

    store = get_store_by_id(store_id)
    table = get_table(store_id, table_num)
    available_games = get_available_games(store_id)
    unavailable_games = get_unavailable_games(store_id)

    return render_template(
        "stores/select_games.html",
        store=store,
        table=table,
        available_games=available_games,
        unavailable_games=unavailable_games,
        start_time=start_time,
        end_time=end_time,
    )


@bp.route(
    "/store/<int:store_id>/table/<int:table_num>/confirm-booking", methods=("POST",)
)
def confirm_booking(store_id, table_num):
    if not g.user:
        return redirect(url_for("auth.login"))

    start_time = request.form.get("start_time", type=int)
    end_time = request.form.get("end_time", type=int)
    selected_games = request.form.getlist("selected_games")

    if not selected_games:
        flash("Please select at least one game.")
        return redirect(
            url_for(
                "stores.select_games",
                store_id=store_id,
                table_num=table_num,
                start_time=start_time,
                end_time=end_time,
            )
        )

    today = str(date.today())
    try:
        game_ids = [int(game_id) for game_id in selected_games]
        create_session(
            g.user["id"], store_id, table_num, today, start_time, end_time, game_ids
        )
        flash(
            f"Session booked! Table {table_num} from {start_time}:00 to {end_time}:00"
        )
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Error booking session: {str(e)}")
        return redirect(
            url_for(
                "stores.select_games",
                store_id=store_id,
                table_num=table_num,
                start_time=start_time,
                end_time=end_time,
            )
        )


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


# Table Functions
def create_table(store_id, capacity):
    db = get_db()
    next_num = db.execute(
        'select coalesce(max(table_num), 0) + 1 from "Table" where store_id = ?',
        (store_id,),
    ).fetchone()[0]
    db.execute(
        'insert into "Table" (store_id, table_num, capacity) values (?, ?, ?)',
        (store_id, next_num, capacity),
    )
    db.commit()
    return next_num


def get_tables(store_id):
    return (
        get_db()
        .execute('select * from "Table" where store_id = ?', (store_id,))
        .fetchall()
    )


def get_table(store_id, table_num):
    return (
        get_db()
        .execute(
            'select * from "Table" where store_id = ? and table_num = ?',
            (store_id, table_num),
        )
        .fetchone()
    )


def delete_table(store_id, table_num):
    db = get_db()
    db.execute(
        'delete from "Table" where store_id = ? and table_num = ?',
        (store_id, table_num),
    )
    db.commit()


def seed_stores():
    users = [("user1", "pass"), ("user2", "pass")]
    user_ids = []
    for username, password in users:
        user_id = create_user(username, password)
        user_ids.append(user_id)

    stores = [
        ("store1", "Big Boy Playhouse", "pass"),
        ("store2", "The Dawg Pen", "pass"),
        ("store3", "The Den", "pass"),
    ]

    store_ids = []
    for username, name, password in stores:
        store_id = create_store(username, name, password, ignore=True)
        store_ids.append(store_id)

    for store_id in store_ids:
        for _ in range(3):
            create_table(store_id, 5)

    # Create new games
    games = ["Freakopoly", "Secret Freak", "Freaknames"]
    game_ids = []
    for game in games:
        game_id = create_game(game)
        game_ids.append(game_id)

    # Add 1-3 copies of games to stores
    for store_id in store_ids:
        for game_id in game_ids:
            n = 1
            for _ in range(n):
                create_game_copy(game_id, store_id)

    today = str(date.today())
    create_session(user_ids[0], store_ids[0], 1, today, 10, 15)
