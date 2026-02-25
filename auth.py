from passlib.context import CryptContext
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional,Annotated

from database import get_db
import models
from models import User


# -------------------------
# Password Hashing (Argon2)
# -------------------------

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------
# Authentication Helpers
# -------------------------

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    user_id: Optional[int] = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = db.get(models.User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def login_user(request: Request, user: models.User) -> None:
    request.session["user_id"] = user.id


def logout_user(request: Request) -> None:
    request.session.clear()
