from d20.db import get_db


def create_script(owner_id, name, code):
    """Create a new trading script.
    
    Args:
        owner_id: MarketParticipant ID (owner of the script)
        name: Name of the script
        code: Script code
        
    Returns:
        The ID of the newly created script
    """
    db = get_db()
    cursor = db.execute(
        "insert into TradingScript (name, code, owner_id) values (?, ?, ?)",
        (name, code, owner_id),
    )
    db.commit()
    return cursor.lastrowid


def get_script(script_id):
    """Get a script by ID."""
    return (
        get_db()
        .execute("select * from TradingScript where id = ?", (script_id,))
        .fetchone()
    )


def get_scripts_by_owner(owner_id):
    """Get all scripts owned by a participant, ordered by name."""
    return (
        get_db()
        .execute(
            "select * from TradingScript where owner_id = ? order by name",
            (owner_id,),
        )
        .fetchall()
    )


def update_script(script_id, name, code):
    """Update a script's name and code.
    
    Args:
        script_id: ID of the script to update
        name: New name
        code: New code
    """
    db = get_db()
    db.execute(
        "update TradingScript set name = ?, code = ? where id = ?",
        (name, code, script_id),
    )
    db.commit()


def delete_script(script_id):
    """Delete a script by ID."""
    db = get_db()
    db.execute("delete from TradingScript where id = ?", (script_id,))
    db.commit()
