from flask import g, render_template

from d20.db.market.market_history import get_all_trades
from d20.db.market.orders import get_inactive_orders_by_participant

from . import bp, market_login_required


@bp.route("/history", methods=("GET",))
@market_login_required
def history():
    participant_id = g.market_participant["id"]
    previous_orders = get_inactive_orders_by_participant(participant_id)
    trades = get_all_trades()
    for t in trades:
        print(dict(t))

    return render_template(
        "market/history.html",
        active_tab="history",
        previous_orders=previous_orders,
        trades=trades,
    )
