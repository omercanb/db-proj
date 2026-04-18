from flask import flash, g, redirect, render_template, request, url_for

from d20.db.game import get_game, get_games
from d20.db.market.orders import (
    cancel_order,
    create_order,
    get_active_orders,
    get_active_orders_by_participant,
)
from d20.db.market.participant_inventory import get_participant_inventory

from . import bp, market_login_required


@bp.route("/trading", methods=("GET", "POST"))
@market_login_required
def trading():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "cancel_order":
            account_cancel_order()
        elif action == "create_limit_buy":
            create_limit_buy_order()
        elif action == "create_market_buy":
            create_market_buy_order()
        elif action == "create_limit_sell":
            create_limit_sell_order()
        elif action == "create_market_sell":
            create_market_sell_order()

        return redirect(url_for("market.trading"))

    participant_id = g.market_participant["id"]
    inventory = get_participant_inventory(participant_id)
    all_games = get_games()
    user_orders = get_active_orders_by_participant(participant_id)
    all_orders = get_active_orders()

    return render_template(
        "market/trading.html",
        active_tab="trading",
        participant=g.market_participant,
        inventory=inventory,
        all_games=all_games,
        user_orders=user_orders,
        all_orders=all_orders,
    )


def account_cancel_order():
    order_id = request.form.get("order_id", type=int)
    try:
        cancel_order(order_id)
        flash("Order cancelled.")
    except Exception as e:
        flash(f"Error cancelling order: {str(e)}")


def create_limit_buy_order():
    game_id = request.form.get("game_id", type=int)
    quantity = request.form.get("quantity", type=int)
    price = request.form.get("price", type=float)

    if game_id is None:
        flash("Please select a game.")
        return
    if quantity is None or quantity <= 0:
        flash("Quantity must be positive.")
        return
    if price is None or price <= 0:
        flash("Price must be positive.")
        return

    try:
        game = get_game(game_id)
        order_id, num_fills, error = create_order(
            participant_id=g.market_participant["id"],
            game_id=game_id,
            order_type="LIMIT",
            side="BUY",
            price=price,
            initial_quantity=quantity,
        )
        if num_fills > 0:
            flash(
                f"BUY order created for {quantity} {game['name']} @ ${price:.2f} - {num_fills} filled immediately!"
            )
        else:
            flash(f"BUY order created for {quantity} {game['name']} @ ${price:.2f}")
    except ValueError as e:
        flash(f"Cannot create order: {str(e)}")
    except Exception as e:
        flash(f"Error creating order: {str(e)}")


def create_market_buy_order():
    game_id = request.form.get("game_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if game_id is None:
        flash("Please select a game.")
        return
    if quantity is None or quantity <= 0:
        flash("Quantity must be positive.")
        return

    try:
        game = get_game(game_id)
        order_id, num_fills, error = create_order(
            participant_id=g.market_participant["id"],
            game_id=game_id,
            order_type="MARKET",
            side="BUY",
            price=None,
            initial_quantity=quantity,
        )
        if error:
            flash(
                f"MARKET BUY order partially filled: {num_fills}/{quantity} {game['name']} - Insufficient liquidity, order cancelled."
            )
        elif num_fills > 0:
            flash(f"MARKET BUY order filled: {num_fills} {game['name']}")
        else:
            flash(
                f"MARKET BUY order failed: No matching sell orders for {game['name']}"
            )
    except ValueError as e:
        flash(f"Cannot create order: {str(e)}")
    except Exception as e:
        flash(f"Error creating order: {str(e)}")


def create_limit_sell_order():
    game_id = request.form.get("game_id", type=int)
    quantity = request.form.get("quantity", type=int)
    price = request.form.get("price", type=float)

    if game_id is None:
        flash("Please select a game.")
        return
    if quantity is None or quantity <= 0:
        flash("Quantity must be positive.")
        return
    if price is None or price <= 0:
        flash("Price must be positive.")
        return

    try:
        game = get_game(game_id)
        order_id, num_fills, error = create_order(
            participant_id=g.market_participant["id"],
            game_id=game_id,
            order_type="LIMIT",
            side="SELL",
            price=price,
            initial_quantity=quantity,
        )
        if num_fills > 0:
            flash(
                f"SELL order created for {quantity} {game['name']} @ ${price:.2f} - {num_fills} filled immediately!"
            )
        else:
            flash(f"SELL order created for {quantity} {game['name']} @ ${price:.2f}")
    except ValueError as e:
        flash(f"Cannot create order: {str(e)}")
    except Exception as e:
        flash(f"Error creating order: {str(e)}")


def create_market_sell_order():
    game_id = request.form.get("game_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if game_id is None:
        flash("Please select a game.")
        return
    if quantity is None or quantity <= 0:
        flash("Quantity must be positive.")
        return

    try:
        game = get_game(game_id)
        order_id, num_fills, error = create_order(
            participant_id=g.market_participant["id"],
            game_id=game_id,
            order_type="MARKET",
            side="SELL",
            price=None,
            initial_quantity=quantity,
        )
        if num_fills > 0:
            flash(f"MARKET SELL order filled: {num_fills} {game['name']}")
        else:
            flash(
                f"MARKET SELL order failed: No matching buy orders for {game['name']}"
            )
    except ValueError as e:
        flash(f"Cannot create order: {str(e)}")
    except Exception as e:
        flash(f"Error creating order: {str(e)}")
