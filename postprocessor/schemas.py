from pydantic import BaseModel


class Extra(BaseModel):
    text: str
    offset: int
    length: int
