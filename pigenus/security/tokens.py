from __future__ import annotations

import hashlib
import secrets


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str, pepper: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        token.encode("utf-8"),
        pepper.encode("utf-8"),
        120_000,
    ).hex()


def verify_token(token: str, token_hash: str, pepper: str) -> bool:
    candidate = hash_token(token, pepper)
    return secrets.compare_digest(candidate, token_hash)

