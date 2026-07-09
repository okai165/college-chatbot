import hashlib


def generate_hash(content: str) -> str:
    """
    Stable SHA256 hash.
    """

    normalized = " ".join(content.split())

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()