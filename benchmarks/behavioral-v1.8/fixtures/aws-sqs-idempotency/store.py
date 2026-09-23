_claimed = set()


def claim(message_id: str) -> bool:
    """Fixture stand-in for an already-wired durable idempotency store."""
    if message_id in _claimed:
        return False
    _claimed.add(message_id)
    return True
