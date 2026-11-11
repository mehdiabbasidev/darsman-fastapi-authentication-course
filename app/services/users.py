from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserProfile


# -------------------------------------------------------------------------
def get_users(session: Session) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    return session.scalars(stmt).all()

# -------------------------------------------------------------------------
def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

# -------------------------------------------------------------------------
def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return session.scalars(stmt).one_or_none()

# -------------------------------------------------------------------------
def create_user(
    session: Session,
    email: str,
    password_hash: str | None = None,
) -> User:
    user = User(email=email, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# -------------------------------------------------------------------------
def update_user(session: Session, user: User, email: str) -> User:
    user.email = email
    session.commit()
    session.refresh(user)
    return user

# -------------------------------------------------------------------------
def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()

# -------------------------------------------------------------------------
def get_profile(session: Session, user_id: int) -> UserProfile | None:
    return session.get(UserProfile, user_id)

