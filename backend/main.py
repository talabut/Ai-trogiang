from fastapi import FastAPI

from backend.api.chat import router as chat_router
from backend.api.upload import router as upload_router
from backend.api.auth import router as auth_router

app = FastAPI(title="AI Trợ Giảng")

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"status": "AI Tutor running"}
