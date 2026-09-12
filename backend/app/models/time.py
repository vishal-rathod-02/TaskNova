from datetime import datetime, timezone


def utcnow():
    """Return a naive UTC timestamp for the existing cross-database schema."""

    return datetime.now(timezone.utc).replace(tzinfo=None)
