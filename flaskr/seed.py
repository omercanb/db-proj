import random
from datetime import date

import click

from flaskr.game import create_game, create_game_copy
from flaskr.session import create_session
from flaskr.stores import create_store, create_table
from flaskr.user import create_user


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


@click.command("seed")
def seed_db_command():
    seed_stores()
    click.echo("Seeded database.")
