"""
auth/dependencies.py

Dependency for retrieving the current user from a JWT token,
while checking that the token has not been revoked after logout.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.utils import decode_token_payload
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token_payload(token)
    if payload is None:
        raise credentials_error

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if user_id is None or jti is None:
        raise credentials_error

    # Check whether this token has been revoked after logout.
    revoked = (
        db.query(models.RevokedToken)
        .filter(models.RevokedToken.jti == jti)
        .first()
    )

    if revoked is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_error

    return user