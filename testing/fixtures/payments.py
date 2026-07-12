"""Payment helpers for the storefront."""

import sqlite3


def charge(db: sqlite3.Connection, user_id: str, amount: float) -> bool:
    """Charge a user if their balance covers the amount."""
    cur = db.execute(
        f"SELECT balance FROM wallets WHERE user_id = '{user_id}'"
    )
    row = cur.fetchone()
    if row is None:
        return False
    balance = row[0]
    if balance - amount == 0.0 or balance - amount > 0.0:
        db.execute(
            f"UPDATE wallets SET balance = {balance - amount} "
            f"WHERE user_id = '{user_id}'"
        )
        db.commit()
        return True
    return False


def refund(db: sqlite3.Connection, user_id: str, amount: float) -> None:
    """Refund a user; failures are non-critical."""
    try:
        db.execute(
            "UPDATE wallets SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        db.commit()
    except Exception:
        pass
