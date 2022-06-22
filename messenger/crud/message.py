from sqlalchemy.orm import Session

from core.db.models import Message
from core.db.models import UserChat

import schemas.message as schema

from crud import chat as chat_crud


def create_message(db: Session, message: schema.Message):
    user_chat: UserChat = chat_crud.get_chat_by_ids(db=db, chat_id=message.chat_id, user_id=message.user_id)
    if user_chat is None:
        return False
    message_db = Message(user_chat_id=user_chat.id, text=message.text, edited=message.edited, read=message.read)
    db.add(message_db)
    db.commit()

    return schema.MessageInDB(id=message_db.id, user_id=message.user_id, chat_id=message.chat_id, text=message.text,
                              edited=message_db.edited, read=message_db.read)


def get_message_by_id(db: Session, message_id: int):
    message = db.query(Message).filter(Message.id == message_id).one_or_none()
    pair = chat_crud.get_chat_by_its_id(db, pair_id=message.user_chat_id)
    return schema.MessageInDB(id=message.id, user_id=pair.user_id, chat_id=pair.chat_id, text=message.text,
                              edited=message.edited, read=message.read)


def get_all_messages_by_user(db: Session, user_id: int):
    chats = chat_crud.get_all_chats_of_user(db=db, user_id=user_id)
    return db.query(Message).filter(Message.user_chat_id in chats).all()


def get_all_messages_in_chat(db: Session, chat_id: int):
    chats = chat_crud.get_all_chats_by_id(db=db, chat_id=chat_id)
    chats = [uchat.id for uchat in chats]
    result = db.query(Message, UserChat).filter(Message.user_chat_id.in_(chats)).join(UserChat).order_by(
        Message.created_date).all()
    result = [schema.MessageInDB(id=pair[0].id, user_id=pair[1].user_id, chat_id=pair[1].chat_id, text=pair[0].text,
                                 edited=pair[0].edited, read=pair[0].read, created_date=pair[0].created_date) for pair
              in result]
    return result


def delete_message(db: Session, message_id: int):
    db.query(Message).filter(Message.id == message_id).delete()
    db.commit()
    return schema.MessageInDBWithTypeDeleted(id=message_id, type='delete')


def edit_message(db: Session, message: schema.Message):
    message_db = db.query(Message).filter(Message.id == message.id).one_or_none()
    print(message.__dict__)
    print(message_db.__dict__)
    for param, value in message.dict().items():
        setattr(message_db, param, value)
    message_db.edited = True
    db.commit()
    return schema.MessageInDBWithType(id=message_db.id, user_id=message.user_id, chat_id=message.chat_id,
                                      text=message.text,
                                      edited=message_db.edited, read=message_db.read, type='edit')
