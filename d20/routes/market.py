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

from d20.db.game import get_game, get_games
from d20.db.market.market_participant import (
    decrement_available_cash,
    get_market_participant,
    get_market_participant_by_customer,
    get_market_participant_by_store,
    increment_available_cash,
)
from d20.db.market.orders import (
    cancel_order,
    create_order,
    get_active_orders,
    get_active_orders_by_participant,
    get_inactive_orders_by_participant,
    get_orders_by_participant,
)
from d20.db.market.participant_inventory import (
    create_participant_inventory,
    delete_market_inventory,
    get_participant_inventory,
    get_participant_inventory_for_game,
    update_available_quantity,
    update_game_quantity,
    update_reserved_quantity,
)

bp = Blueprint("market", __name__, url_prefix="/market")


@bp.before_app_request
def load_logged_in_market_participant():
    store_id = session.get("store_id")
    user_id = session.get("user_id")
    participant_data = None

    if store_id is not None:
        participant_data = get_market_participant_by_store(store_id)
    elif user_id is not None:
        participant_data = get_market_participant_by_customer(user_id)

    if participant_data:
        g.market_participant = get_market_participant(participant_data["id"])
    else:
        g.market_participant = None


def market_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.market_participant is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.route("/account", methods=("GET", "POST"))
@market_login_required
def account():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "load_cash":
            account_load_cash()
        elif action == "withdraw_cash":
            account_withdraw_cash()
        elif action == "add_inventory":
            account_add_inventory()
        elif action == "remove_available":
            account_remove_available()
        elif action == "remove_inventory":
            account_remove_inventory()
        elif action == "cancel_order":
            account_cancel_order()
        elif action == "create_limit_buy":
            create_limit_buy_order()
        elif action == "create_market_buy":
            create_market_buy_order()
        elif action == "create_limit_sell":
            create_limit_sell_order()
        elif action == "create_market_sell":
            create_market_sell_order()

        return redirect(url_for("market.account"))

    participant_id = g.market_participant["id"]
    inventory = get_participant_inventory(participant_id)
    all_games = get_games()
    user_orders = get_active_orders_by_participant(participant_id)
    previous_orders = get_inactive_orders_by_participant(participant_id)
    all_orders = get_active_orders()

    return render_template(
        "market/account.html",
        participant=g.market_participant,
        inventory=inventory,
        all_games=all_games,
        user_orders=user_orders,
        previous_orders=previous_orders,
        all_orders=all_orders,
    )


def account_load_cash():
    amount = request.form.get("amount", type=float)
    if amount is None or amount <= 0:
        flash("Amount must be positive.")
    else:
        try:
            increment_available_cash(g.market_participant["id"], amount)
            flash(f"Loaded ${amount:.2f} successfully.")
        except Exception as e:
            flash(f"Error loading cash: {str(e)}")


def account_withdraw_cash():
    amount = request.form.get("amount", type=float)
    if amount is None or amount <= 0:
        flash("Amount must be positive.")
    else:
        try:
            decrement_available_cash(g.market_participant["id"], amount)
            flash(f"Withdrew ${amount:.2f} successfully.")
        except ValueError as e:
            flash(f"Cannot withdraw: {str(e)}")
        except Exception as e:
            flash(f"Error withdrawing cash: {str(e)}")


def account_add_inventory():
    game_id = request.form.get("game_id", type=int)
    num_to_add = request.form.get("qty_to_add", type=int)

    if game_id is None:
        flash("Please select a game.")
    elif num_to_add is None:
        flash("Quantity is required.")
    elif num_to_add < 0:
        flash("Quantity must be non-negative.")
    else:
        try:
            existing_inventory = get_participant_inventory_for_game(
                g.market_participant["id"], game_id
            )
            game = get_game(game_id)
            game_name = game["name"]
            if existing_inventory:
                available_quantity = existing_inventory["available_quantity"]
                update_available_quantity(
                    g.market_participant["id"],
                    game_id,
                    available_quantity + num_to_add,
                )
                if num_to_add == 1:
                    flash(f"Successfully added {num_to_add} copy of {game_name}.")
                else:
                    flash(f"Successfully added {num_to_add} copies of {game_name}.")
            else:
                create_participant_inventory(
                    g.market_participant["id"], game_id, num_to_add, 0
                )
                if num_to_add == 1:
                    flash(f"Successfully added {num_to_add} copy of {game_name}.")
                else:
                    flash(f"Successfully added {num_to_add} copies of {game_name}.")
        except Exception as e:
            raise e
            flash(f"Error adding game: {str(e)}")


def account_remove_available():
    game_id = request.form.get("game_id", type=int)
    quantity_to_remove = request.form.get("quantity_to_remove", type=int)

    if game_id is None or quantity_to_remove is None:
        flash("Please provide all required information.")
    elif quantity_to_remove <= 0:
        flash("Quantity must be positive.")
    else:
        try:
            inventory = get_participant_inventory_for_game(
                g.market_participant["id"], game_id
            )
            if not inventory:
                flash("Game not found in inventory.")
            elif inventory["available_quantity"] < quantity_to_remove:
                flash(
                    f"Cannot remove {quantity_to_remove} copies. Only {inventory['available_quantity']} available."
                )
            else:
                new_available = inventory["available_quantity"] - quantity_to_remove
                update_available_quantity(
                    g.market_participant["id"], game_id, new_available
                )
                if quantity_to_remove == 1:
                    flash(f"Removed {quantity_to_remove} copy from the market.")
                else:
                    flash(f"Removed {quantity_to_remove} copies from market.")
        except Exception as e:
            flash(f"Error removing games: {str(e)}")


def account_remove_inventory():
    game_id = request.form.get("game_id", type=int)
    if game_id is None:
        flash("Invalid game.")
    else:
        try:
            delete_market_inventory(g.market_participant["id"], game_id)
            flash("Game removed from inventory.")
        except Exception as e:
            flash(f"Error removing game: {str(e)}")


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
