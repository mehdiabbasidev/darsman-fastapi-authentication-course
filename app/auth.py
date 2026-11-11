from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.services import auth as auth_service
from app.services import users as user_service

# --------------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --------------------------------------------------------------------------------
def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
    ) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not validate credentials or Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = auth_service.decode_access_token(token)
        user_id = int(payload.get("sub",""))
        
    except ExpiredSignatureError:
        raise credentials_exception
    
    except (InvalidTokenError, TypeError, ValueError):
        raise credentials_exception


    user = user_service.get_user(session, user_id)
    if user is None:
        raise credentials_exception

    return user
