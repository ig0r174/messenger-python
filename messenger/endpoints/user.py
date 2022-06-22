from fastapi import APIRouter, Depends, HTTPException, status

from deps import get_db, get_current_user
import crud.user as crud
from schemas.user import User, UserInDB, UserCreate


router = APIRouter(prefix="/user")


@router.get("/", response_model=UserInDB)
async def get_user(user_id=Depends(get_current_user), db=Depends(get_db)):
    """Получить пользователя по заданному user_id"""
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@router.post("/", response_model=UserInDB)
async def create_user(user: UserCreate, db=Depends(get_db)):
    """Создать пользователя"""
    result = crud.create_user(db=db, user=user)
    return result


@router.put("/", response_model=UserInDB)
async def update_user(user: User, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Изменить пользователя"""
    user_db = crud.update_user(db=db, user_id=user_id, user=user)

    return user_db


@router.delete("/")
async def delete_user(user_id=Depends(get_current_user), db=Depends(get_db)):
    """Удалить пользователя"""
    crud.delete_user(db=db, message_id=user_id)
