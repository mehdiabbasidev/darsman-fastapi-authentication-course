from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserProfile


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

# -------------------------------------------------------------------------
def save_profile(session: Session, user_id: int, full_name: str | None = None, 
                 avatar_url: str | None = None, bio: str | None = None,) -> UserProfile:
    
    profile = get_profile(session, user_id)
    if profile is None:
        profile = UserProfile(
            user_id=user_id,
            full_name=full_name,
            avatar_url=avatar_url,
            bio=bio,
        )
        session.add(profile)
    else:
        if full_name is not None:
            profile.full_name = full_name
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if bio is not None:
            profile.bio = bio

    session.commit()
    session.refresh(profile)
    return profile
