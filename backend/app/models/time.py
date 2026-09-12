from datetime import datetime, timezone


def utcnow():
    """Return a naive UTC timestamp for the existing cross-database schema."""

    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso_utc(value):
    """Serialize a UTC timestamp with an explicit zone designator.

    Browsers parse zone-less ISO strings as *local* time, which shifted every
    displayed timestamp by the viewer's UTC offset. The stored values are UTC
    by construction (see utcnow), so mark them as such and let the frontend
    convert to local time.
    """

    if value is None:
        return None
    return value.isoformat() + "Z"
