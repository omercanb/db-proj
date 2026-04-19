from flask import g, jsonify, render_template, request

from d20.db.market.orders import get_orders_by_script
from d20.db.market.trading_scripts import (
    create_script,
    delete_script,
    get_script,
    update_script,
)

from . import bp, market_login_required


@bp.route("/algorithmic/scripts/orders/<int:script_id>", methods=("GET",))
@market_login_required
def get_script_orders(script_id):
    script = get_script(script_id)
    if not script:
        return jsonify({"success": False, "error": "Script not found"}), 404

    # Verify ownership
    if script["owner_id"] != g.market_participant["id"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    orders = get_orders_by_script(script_id)
    if orders:
        orders = [dict(order) for order in orders]
        return jsonify({"success": True, "data": orders})
    else:
        return jsonify({"success": False, "error": "An error occured."}), 500


@bp.route("/algorithmic/scripts", methods=("POST",))
@market_login_required
def create_script_endpoint():
    """Create a new trading script."""
    participant_id = g.market_participant["id"]
    data = request.json
    name = data.get("name", "Untitled Script")
    code = data.get("code", "")

    try:
        script_id = create_script(participant_id, name, code)
        script = get_script(script_id)
        return jsonify({"success": True, "script": dict(script)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@bp.route("/algorithmic/scripts/<int:script_id>", methods=("GET",))
@market_login_required
def get_script_endpoint(script_id):
    """Get a script by ID."""
    script = get_script(script_id)
    if not script:
        return jsonify({"success": False, "error": "Script not found"}), 404

    # Verify ownership
    if script["owner_id"] != g.market_participant["id"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    return jsonify({"success": True, "script": dict(script)})


@bp.route("/algorithmic/scripts/<int:script_id>", methods=("PUT",))
@market_login_required
# Save script
def update_script_endpoint(script_id):
    """Update a script's name and code."""
    script = get_script(script_id)
    if not script:
        return jsonify({"success": False, "error": "Script not found"}), 404

    # Verify ownership
    if script["owner_id"] != g.market_participant["id"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.json
    name = data.get("name", script["name"])
    code = data.get("code", script["code"])

    try:
        update_script(script_id, name, code)
        updated_script = get_script(script_id)
        return jsonify({"success": True, "script": dict(updated_script)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@bp.route("/algorithmic/scripts/<int:script_id>", methods=("DELETE",))
@market_login_required
def delete_script_endpoint(script_id):
    """Delete a script."""
    script = get_script(script_id)
    if not script:
        return jsonify({"success": False, "error": "Script not found"}), 404

    # Verify ownership
    if script["owner_id"] != g.market_participant["id"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    try:
        delete_script(script_id)
        return jsonify({"success": True, "message": "Script deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
