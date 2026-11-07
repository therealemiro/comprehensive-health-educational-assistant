"""
auth/routes.py

Endpoints for user registration, login with rate limiting to prevent brute-force attacks,
and secure logout by revoking the token instead of simply removing it on the client side.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth.utils import hash_password, verify_password, create_access_token, decode_token_payload
from app.auth.dependencies import oauth2_scheme
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="This email is already registered.")

    user = models.User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")  # Limit each IP address to 5 login attempts per minute to prevent brute-force attacks.
def login(request: Request, credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_access_token(user_id=user.id)
    return schemas.Token(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Unlike simply deleting the token on the client side, this endpoint revokes the token's
    JTI in the database, ensuring that the token cannot be used even if someone obtains it
    before its expiration.
    """
    payload = decode_token_payload(token)
    if payload is None or payload.get("jti") is None:
        raise HTTPException(status_code=401, detail="Invalid token.")

    already_revoked = db.query(models.RevokedToken).filter(
        models.RevokedToken.jti == payload["jti"]
    ).first()

    if not already_revoked:
        db.add(models.RevokedToken(jti=payload["jti"]))
        db.commit()