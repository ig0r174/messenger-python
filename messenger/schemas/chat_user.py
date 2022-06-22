from pydantic import BaseModel


class ChatUser(BaseModel):
    user_id: int
    chat_id: int


class ChatAddUser(BaseModel):
    login: str
    chat_id: int


class ChatUserInDB(ChatUser):
    id: int

    class Config:
        orm_mode = True
