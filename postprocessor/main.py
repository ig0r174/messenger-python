from typing import List

from fastapi import FastAPI, Body, APIRouter
import uvicorn

import domain.parsing as domain
from schemas import Extra


app = FastAPI()

@app.post("/extra", response_model=List[Extra])
def get_extra(text: str = Body(..., embed=True)):
    """Получает экстра-данные из текста"""
    return domain.get_extra(text)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8080,
        reload=True,
        debug=True,
    )
