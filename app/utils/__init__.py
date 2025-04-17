from datetime import datetime, timezone

def get_current_timestamp() -> datetime:
    """
    Returns current UTC timestamp with timezone info
    """
    return datetime.now(timezone.utc)