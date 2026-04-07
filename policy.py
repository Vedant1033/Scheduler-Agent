"""Policy database helpers."""

from config import MOCK_POLICIES


def lookup_policy(query: str) -> dict | None:
    """Return policy dict if query matches a policy ID or holder first name."""
    q = query.upper()
    for pid, info in MOCK_POLICIES.items():
        if pid in q or info["holder"].split()[0].lower() in query.lower():
            return {"id": pid, **info}
    return None
