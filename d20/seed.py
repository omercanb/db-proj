import random
from datetime import date

import click

from d20.db.game import create_game, create_game_copy
from d20.db.market.market_participant import (
    get_market_participant,
    get_market_participant_by_customer,
    increment_available_cash,
)
from d20.db.market.orders import create_order
from d20.db.market.participant_inventory import increment_available_quantity
from d20.db.session import create_session
from d20.db.stores import create_store, create_table
from d20.db.user import create_user, get_user_by_id


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
        store_id = create_store(username, name, password)
        store_ids.append(store_id)

    for store_id in store_ids:
        for _ in range(3):
            create_table(store_id, 5)

    # Create new games
    games = ["Freakopoly", "Secret Freak", "Freaknames"]
    symbols = ["FRKPOL", "SCRTFRK", "FRKNMS"]
    game_ids = []
    for game, symbol in zip(games, symbols):
        game_id = create_game(game, symbol)
        game_ids.append(game_id)

    # Add 1-3 copies of games to stores
    store_to_game_copy = {}
    for store_id in store_ids:
        store_to_game_copy[store_id] = []
        for game_id in game_ids:
            n = 1
            for _ in range(n):
                copy_num = create_game_copy(game_id, store_id)
                store_to_game_copy[store_id].append((game_id, copy_num))

    # TODO refactor into another function
    user1 = user_ids[0]
    store1 = store_ids[0]
    table_num = 1
    day = str(date.today())
    start = 10
    end = 15
    games_used = [copy_num for game_id, copy_num in store_to_game_copy[store1][:1]]
    create_session(user1, store1, table_num, day, start, end, games_used)

    # Seed some active trades from user1
    user1_market = get_market_participant_by_customer(user1)["id"]

    # Buy 2 copies of game 1 for 20 dollars (needs available cash to reserve)
    increment_available_cash(user1_market, 100)
    game1 = game_ids[0]
    create_order(user1_market, game1, "LIMIT", "BUY", 20, 2)

    # Sell 3 copies of game 2 for 30 dollars (needs available inventory)
    game2 = game_ids[1]
    increment_available_quantity(
        user1_market,
        game2,
        3,
    )
    create_order(user1_market, game2, "LIMIT", "SELL", 30, 3)


@click.command("seed")
def seed_db_command():
    seed_stores()
    click.echo("Seeded database.")
