from fastapi import APIRouter, HTTPException, Response, Body, Depends, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.services import users as user_service
from app.dependencies.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])


# --------------------------------------------------------------------------------
def ensure_owner(user_id: int, current_user: User) -> None:
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own account",
        )
    
# --------------------------------------------------------------------------------
# GET /users
@router.get("")
def get_users(session: Session = Depends(get_session)):
    users = user_service.get_users(session)
    return [user.to_dict() for user in users]


# --------------------------------------------------------------------------------
# GET /users/{user_id}
@router.get("/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = user_service.get_user(session, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user.to_dict()
    


# # --------------------------------------------------------------------------------
# # POST /users
@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(data: dict = Body(...), session: Session = Depends(get_session)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    if user_service.get_user_by_email(session, email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user = user_service.create_user(session, email)
    return user.to_dict()




# --------------------------------------------------------------------------------
# PUT /users/{user_id}
@router.put("/{user_id}")
def update_user(
    user_id: int, 
    data: dict = Body(...), 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    ):
    ensure_owner(user_id, current_user)
    user = user_service.get_user(session, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    existing_user = user_service.get_user_by_email(session, email)
    if existing_user and existing_user.id != user_id:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = user_service.update_user(session, user, email)
    return user.to_dict()


# --------------------------------------------------------------------------------

# DELETE /users/{user_id}
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    ):

    ensure_owner(user_id, current_user)
    user = user_service.get_user(session, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_service.delete_user(session, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)



# --------------------------------------------------------------------------------
@router.get("/{user_id}/profile")
def get_user_profile(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_owner(user_id, current_user)
    
    if user_service.get_user(session, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile = user_service.get_profile(session, user_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return profile.to_dict()


# --------------------------------------------------------------------------------
# PUT /users/{user_id}/profile
@router.put("/{user_id}/profile")
def update_user_profile(
    user_id: int,
    data: dict = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_owner(user_id, current_user)
    
    if user_service.get_user(session, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    current_profile = user_service.get_profile(session, user_id)

    if current_profile is None and not data.get("full_name"):
        raise HTTPException(
            status_code=400,
            detail="full_name is required when creating a profile",
        )

    if "full_name" in data and not data["full_name"]:
        raise HTTPException(status_code=400, detail="full_name cannot be empty")

    profile = user_service.save_profile(
        session,
        user_id=user_id,
        full_name=data.get("full_name"),
        avatar_url=data.get("avatar_url"),
        bio=data.get("bio"),
    )

    return profile.to_dict()
