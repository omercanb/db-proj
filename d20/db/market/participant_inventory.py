from d20.db import get_db


def create_participant_inventory(
    participant_id, game_id, available_quantity=0, reserved_quantity=0
):
    """Create or initialize market inventory for a participant and game.

    Args:
        participant_id: ID of the market participant
        game_id: ID of the game
        available_quantity: Initial available quantity
        reserved_quantity: Initial reserved quantity
    """
    db = get_db()
    db.execute(
        "insert into MarketParticipantInventory (participant_id, game_id, available_quantity, reserved_quantity) values (?, ?, ?, ?)",
        (participant_id, game_id, available_quantity, reserved_quantity),
    )
    db.commit()


def get_participant_inventory(participant_id):
    """Get all inventory items for a participant."""
    return (
        get_db()
        .execute(
            "select * from MarketParticipantInventory join Game on (game_id = id) where participant_id = ?",
            (participant_id,),
        )
        .fetchall()
    )


def get_participant_inventory_for_game(participant_id, game_id):
    """Get inventory for a specific participant and game."""
    return (
        get_db()
        .execute(
            "select * from MarketParticipantInventory where participant_id = ? and game_id = ?",
            (participant_id, game_id),
        )
        .fetchone()
    )


def get_game_inventory_count(game_id):
    """Get total quantity (available + reserved) of a game across all participants."""
    return (
        get_db()
        .execute(
            "select sum(available_quantity + reserved_quantity) as total from MarketParticipantInventory where game_id = ?",
            (game_id,),
        )
        .fetchone()[0]
    )


def update_available_quantity(participant_id, game_id, quantity):
    """Set the available quantity for a participant's game. Auto-creates if doesn't exist."""
    db = get_db()
    inventory = get_participant_inventory_for_game(participant_id, game_id)

    if not inventory:
        # Create with available=quantity, reserved=0
        db.execute(
            "insert into MarketParticipantInventory (participant_id, game_id, available_quantity, reserved_quantity) values (?, ?, ?, ?)",
            (participant_id, game_id, quantity, 0),
        )
    else:
        db.execute(
            "update MarketParticipantInventory set available_quantity = ? where participant_id = ? and game_id = ?",
            (quantity, participant_id, game_id),
        )
        # Check if we should delete (both quantities are 0)
        if quantity == 0 and inventory["reserved_quantity"] == 0:
            delete_market_inventory(participant_id, game_id)
            db.commit()
            return

    db.commit()


def update_reserved_quantity(participant_id, game_id, quantity):
    """Set the reserved quantity for a participant's game. Auto-creates if doesn't exist."""
    db = get_db()
    inventory = get_participant_inventory_for_game(participant_id, game_id)

    if not inventory:
        # Create with reserved=quantity, available=0
        db.execute(
            "insert into MarketParticipantInventory (participant_id, game_id, available_quantity, reserved_quantity) values (?, ?, ?, ?)",
            (participant_id, game_id, 0, quantity),
        )
    else:
        db.execute(
            "update MarketParticipantInventory set reserved_quantity = ? where participant_id = ? and game_id = ?",
            (quantity, participant_id, game_id),
        )
        # Check if we should delete (both quantities are 0)
        if inventory["available_quantity"] == 0 and quantity == 0:
            delete_market_inventory(participant_id, game_id)
            db.commit()
            return

    db.commit()


def update_game_quantity(
    participant_id, game_id, available_quantity, reserved_quantity
):
    """Update both available and reserved quantities. Auto-creates if doesn't exist."""
    if available_quantity == 0 and reserved_quantity == 0:
        delete_market_inventory(participant_id, game_id)
        return

    db = get_db()
    inventory = get_participant_inventory_for_game(participant_id, game_id)

    if not inventory:
        # Create with both quantities
        db.execute(
            "insert into MarketParticipantInventory (participant_id, game_id, available_quantity, reserved_quantity) values (?, ?, ?, ?)",
            (participant_id, game_id, available_quantity, reserved_quantity),
        )
    else:
        db.execute(
            "update MarketParticipantInventory set available_quantity = ?, reserved_quantity = ? where participant_id = ? and game_id = ?",
            (available_quantity, reserved_quantity, participant_id, game_id),
        )

    db.commit()


def increment_available_quantity(participant_id, game_id, amount):
    """Increase available quantity for a participant's game. Auto-creates if doesn't exist.

    Args:
        participant_id: Market participant ID
        game_id: Game ID
        amount: Amount to add to available_quantity
    """
    inventory = get_participant_inventory_for_game(participant_id, game_id)
    current_available = inventory["available_quantity"] if inventory else 0

    new_available = current_available + amount
    if new_available < 0:
        raise ValueError("Available quantity cannot be negative")

    update_available_quantity(participant_id, game_id, new_available)


def decrement_available_quantity(participant_id, game_id, amount):
    """Decrease available quantity for a participant's game. Auto-creates if doesn't exist.

    Args:
        participant_id: Market participant ID
        game_id: Game ID
        amount: Amount to subtract from available_quantity
    """
    inventory = get_participant_inventory_for_game(participant_id, game_id)
    current_available = inventory["available_quantity"] if inventory else 0

    new_available = current_available - amount
    if new_available < 0:
        raise ValueError(
            f"Cannot decrease available quantity by {amount}. Only {current_available} available."
        )

    update_available_quantity(participant_id, game_id, new_available)


def increment_reserved_quantity(participant_id, game_id, amount):
    """Increase reserved quantity for a participant's game. Auto-creates if doesn't exist.

    Args:
        participant_id: Market participant ID
        game_id: Game ID
        amount: Amount to add to reserved_quantity
    """
    inventory = get_participant_inventory_for_game(participant_id, game_id)
    current_reserved = inventory["reserved_quantity"] if inventory else 0

    new_reserved = current_reserved + amount
    if new_reserved < 0:
        raise ValueError("Reserved quantity cannot be negative")

    update_reserved_quantity(participant_id, game_id, new_reserved)


def decrement_reserved_quantity(participant_id, game_id, amount):
    """Decrease reserved quantity for a participant's game. Auto-creates if doesn't exist.

    Args:
        participant_id: Market participant ID
        game_id: Game ID
        amount: Amount to subtract from reserved_quantity
    """
    inventory = get_participant_inventory_for_game(participant_id, game_id)
    current_reserved = inventory["reserved_quantity"] if inventory else 0

    new_reserved = current_reserved - amount
    if new_reserved < 0:
        raise ValueError(
            f"Cannot decrease reserved quantity by {amount}. Only {current_reserved} reserved."
        )

    update_reserved_quantity(participant_id, game_id, new_reserved)


def delete_market_inventory(participant_id, game_id):
    """Delete inventory entry for a participant and game."""
    db = get_db()
    db.execute(
        "delete from MarketParticipantInventory where participant_id = ? and game_id = ?",
        (participant_id, game_id),
    )
    db.commit()
