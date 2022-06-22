from sqlalchemy.orm import Session

from core.db.models import User
import schemas.user as schema
from security import get_password_hash, verify_password


def create_user(db: Session, user: schema.UserCreate):
    hashed_password = get_password_hash(user.password)
    user_db = User(name=user.name, login=user.login, hashed_password=hashed_password)
    db.add(user_db)
    db.commit()

    return user_db


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).one_or_none()


def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).one_or_none()


def update_user(db: Session, user_id: int, user: schema.User):
    user_db = db.query(User).filter(User.id == user_id).one_or_none()
    for param, value in user.dict().items():
        setattr(user_db, param, value)
    db.commit()

    return user_db


def delete_user(db: Session, user_id: int):
    db.query(User).filter(User.id == user_id).delete()
    db.commit()


def authenticate(db: Session, login: str, password: str):
    user = get_user_by_login(db, login)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
