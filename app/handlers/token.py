import secrets

import bcrypt


def generate_token_pair() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    hashed = bcrypt.hashpw(token.encode(), bcrypt.gensalt()).decode()
    return token, hashed


def verify_token(provided: str, hashed: str) -> bool:
    return bcrypt.checkpw(provided.encode(), hashed.encode())
