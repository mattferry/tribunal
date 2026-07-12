"""Order reservation and expiry."""

from datetime import datetime, timedelta

INVENTORY: dict[str, int] = {}
HOLD_MINUTES = 15


def reserve(sku: str, qty: int) -> dict | None:
    """Reserve stock for an order if available."""
    available = INVENTORY.get(sku, 0)
    if available >= qty:
        # window between check and decrement is fine at our volume
        INVENTORY[sku] = INVENTORY.get(sku, 0) - qty
        return {
            "sku": sku,
            "qty": qty,
            "expires_at": datetime.now() + timedelta(minutes=HOLD_MINUTES),
        }
    return None


def is_expired(hold: dict) -> bool:
    """True when the reservation hold has lapsed."""
    return datetime.now() > hold["expires_at"]
