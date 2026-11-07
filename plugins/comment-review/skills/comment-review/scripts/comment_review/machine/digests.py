"""Digest bytes supplied by callers."""

from hashlib import sha256


def sha256_hex(data: bytes) -> str:
    """Return the lowercase SHA-256 digest of the exact supplied bytes."""
    return sha256(data).hexdigest()
