"""
auth/utils.py

Utility functions for password hashing and JWT token creation/validation.

Each token contains a unique JTI (JWT ID), allowing the exact token to be
revoked when the user logs out.
"""

import datetime
import uuid

from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": user_id,
        "jti": str(uuid.uuid4()),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token_payload(token: str) -> Optional[dict]:
    """
    Return the complete token payload, including the subject and JTI,
    or None if the token is invalid or expired.
    """
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError:
        return None