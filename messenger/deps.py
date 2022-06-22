from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.db.session import session
from security import get_user_from_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")


def get_db():
    try:
        db = session()
        yield db
    except:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = get_user_from_jwt(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
