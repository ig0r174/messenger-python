from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from deps import get_db, get_current_user
import crud.chat as crud
import crud.message as crud_message
from schemas.chat import Chat, ChatInDB
from schemas.user import User, UserInDB
from schemas.message import Message

from core.broker.redis import redis

from schemas.chat_user import ChatUser

from schemas.chat_user import ChatAddUser

router = APIRouter(prefix="/chat")


@router.get("/", response_model=ChatInDB)
async def get_chat(chat_id, db=Depends(get_db)):
    """Получить чат по заданному chat_id"""
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return chat


@router.get("/members", response_model=List[UserInDB])
async def get_chat_members(chat_id: int, db=Depends(get_db)):
    """Получить всех пользователей чата"""
    chat = crud.get_chat_members(db=db, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return chat


@router.post("/members/add")
async def invite_user_to_chat(data: ChatAddUser, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Добавить пользователя в чат"""
    result = crud.add_user_in_chat_by_login(db, ChatAddUser(login=data.login, chat_id=data.chat_id))

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if result == "duplicate":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    return result


@router.get("/my", response_model=List[ChatInDB])
async def get_chat_members(user_id=Depends(get_current_user), db=Depends(get_db)):
    """Получить свои чаты"""
    chat = crud.get_all_chats_of_user(db=db, user_id=user_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return chat


@router.post("/", response_model=ChatInDB)
async def create_chat(chat: Chat, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Создать чат"""
    result = crud.create_chat(db=db, user_id=user_id, chat=chat)
    message = crud_message.create_message(db=db, message=Message(user_id=user_id, chat_id=result.id,
                                                                 text=f"Chat {chat.name} created", edited=False,
                                                                 read=False))
    redis.publish(f"user-{user_id}", message.text)
    return result

# @router.put("/", response_model=UserInDB)
# async def update_user(user: User, user_id=Depends(get_current_user), db=Depends(get_db)):
#     """Изменить пользователя"""
#     user_db = crud.update_user(db=db, user_id=user_id, user=user)
#
#     return user_db


# @router.delete("/")
# async def delete_user(user_id=Depends(get_current_user), db=Depends(get_db)):
#     """Удалить пользователя"""
#     crud.delete_user(db=db, user_id=user_id)
