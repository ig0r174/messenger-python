from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from endpoints.login import router as login_router
from endpoints.user import router as user_router
from endpoints.utils import router as utils_router
from endpoints.chat import router as chat_router
from endpoints.message import router as message_router

app = FastAPI()

app.include_router(user_router, tags=["user"])
app.include_router(login_router, tags=["login"])
app.include_router(utils_router, tags=["utils"])
app.include_router(chat_router, tags=["chat"])
app.include_router(message_router, tags=["message"])
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=8080,
        reload=True,
        debug=True,
    )
