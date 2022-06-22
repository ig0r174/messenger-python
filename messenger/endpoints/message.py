import threading

from fastapi import APIRouter, Depends, HTTPException, status

from deps import get_db, get_current_user
import crud.message as crud
import crud.chat as chat_crud
from schemas.message import Message, MessageInDB
from core.broker.redis import redis

from schemas.message import MessageInDBWithTypeDeleted

mutex = threading.Lock()

import json

from utils import async_query

router = APIRouter(prefix="/message")


@router.get("/", response_model=MessageInDB)
async def get_message(message_id, db=Depends(get_db)):  # user_id=Depends(get_current_user)
    """Получить сообщение по заданному chat_id"""
    message = crud.get_message_by_id(db=db, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return message


@router.get("/allMy", response_model=(MessageInDB))
async def get_all_messages(user_id=Depends(get_current_user), db=Depends(get_db)):
    """Получить все сообщения пользователя"""
    messages = crud.get_all_messages_by_user(db=db, user_id=user_id)
    if messages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return messages


@router.get("/allInChat", response_model=MessageInDB)
async def get_all_messages(chat_id: int, db=Depends(get_db)):
    """Получить все сообщения в чате"""
    messages = crud.get_all_messages_in_chat(db=db, chat_id=chat_id)
    if messages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return messages


@router.post("/", response_model=MessageInDB)
async def create_message(message: Message, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Отправить сообщение"""
    message.user_id = user_id
    mutex.acquire()
    message.text = await process_message(message.text)
    mutex.release()
    result = crud.create_message(db=db, message=message)
    await redis.publish(f"chat-{message.chat_id}", result.toJSON())
    return result


@router.delete("/", response_model=MessageInDBWithTypeDeleted)
async def delete_message(message_id: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Удалить сообщение"""
    message = crud.get_message_by_id(db=db, message_id=message_id)
    if str(message.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{message.user_id} != {user_id}")
    res = crud.delete_message(db=db, message_id=message_id)
    await redis.publish(f"chat-{message.chat_id}", res.toJSON())
    return res


@router.put("/", response_model=Message)
async def edit_message(message: MessageInDB, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Изменить сообщение"""
    if str(message.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    mutex.acquire()
    message.text = await process_message(message.text)
    mutex.release()
    message_db = crud.edit_message(db=db, message=message)
    await redis.publish(f"chat-{message.chat_id}", message_db.toJSON())
    return message_db


async def process_message(text: str):
    url = "http://127.0.0.1:8080/extra"

    try:
        extra = await async_query(task_url=url, text=text)
    except BaseException as e:
        print(e)
        return text
    for one in extra:
        if one['type'] == 'link':
            text = text.replace(one['text'], f"<a href='{one['text']}' target=\"_blank\">{one['text']}</a>")
        elif one['type'] == 'hashtag':
            text = text.replace(one['text'],
                                f"<a href='https://www.google.com/search?q={one['text'][1:]}' target=\"_blank\">{one['text']}</a>")
        elif one['type'] == 'mention':
            text = text.replace(one['text'],
                                f"<a href='https://t.me/{one['text'][1:]}' target=\"_blank\">{one['text']}</a>")
    return text
