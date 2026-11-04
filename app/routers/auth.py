from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models import User
from app.services import auth as auth_service
from app.services import users as user_service


router = APIRouter(prefix="/auth", tags=["auth"])


# --------------------------------------------------------------------------------
# POST /auth/register
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    data: dict = Body(...),
    session: Session = Depends(get_session),
):
    email = data.get("email")
    password = data.get("password")

    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    if not password:
        raise HTTPException(status_code=400, detail="password is required")

    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="password must be at least 6 characters",
        )

    if user_service.get_user_by_email(session, email):
        raise HTTPException(status_code=400, detail="Email already exists")

    password_hash = auth_service.hash_password(password)
    user = user_service.create_user(session, email, password_hash)

    return user.to_dict()


# --------------------------------------------------------------------------------
# POST /auth/login
# OAuth2PasswordRequestForm uses the field name `username`.
# In this project, we use that field for the user's email address.
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = auth_service.authenticate_user(
        session,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# --------------------------------------------------------------------------------
# GET /auth/me
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()
