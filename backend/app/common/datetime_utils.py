from datetime import datetime, timezone


def ensure_utc(value: datetime | None) -> datetime | None:
    """Normalizes SQLite-returned naive datetimes to timezone-aware UTC values."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
