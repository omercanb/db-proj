from dataclasses import dataclass
from typing import Any, List

from flask import g, jsonify, render_template, request
from plox.types.lox_callable import LoxCallable

from d20.db import game
from d20.db.game import get_game_by_symbol, get_game_id_by_symbol
from d20.db.market.market_history import get_price
from d20.db.market.orders import create_order


class GetPrice(LoxCallable):
    def arity(self):
        # (SYMBOL)
        return 1

    def call(self, interpreter, arguments: List[Any]):
        symbol = arguments[0]
        price = get_price(symbol)
        return price

    def __str__(self) -> str:
        return "<native get_price>"


# class GetMaxBuyPrice(LoxCallable):
#     def arity(self):
#         # (SYMBOL)
#         return 1
#
#     def call(self, interpreter, arguments: List[Any]):
#         symbol = arguments[0]
#         price = get_price(symbol)
#         return price
#
#     def __str__(self) -> str:
#         return "<native get_price>"


@dataclass
class MarketBuy(LoxCallable):
    script_id: int

    def arity(self):
        # (SYMBOL, quantity)
        return 2

    def call(self, interpreter, arguments: List[Any]):
        symbol = arguments[0]
        quantity = arguments[1]
        game_id = get_game_id_by_symbol(symbol)
        participant_id = g.market_participant["id"]
        order_id, fills, error = create_order(
            participant_id, game_id, "MARKET", "BUY", None, quantity, self.script_id
        )
        return fills

    def __str__(self) -> str:
        return "<native market_buy>"


@dataclass
class MarketSell(LoxCallable):
    script_id: int

    def arity(self):
        # (SYMBOL, quantity)
        return 2

    def call(self, interpreter, arguments: List[Any]):
        symbol = arguments[0]
        quantity = arguments[1]
        game_id = get_game_id_by_symbol(symbol)
        participant_id = g.market_participant["id"]
        order_id, fills, error = create_order(
            participant_id, game_id, "MARKET", "SELL", None, quantity, self.script_id
        )
        return fills

    def __str__(self) -> str:
        return "<native market_sell>"
