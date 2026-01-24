from fastapi import FastAPI

from backend.api.chat import router as chat_router
from backend.api.upload import router as upload_router
from backend.api.auth import router as auth_router
from backend.api.pedagogy import router as pedagogy_router
from backend.api.eval import router as eval_router
from backend.api.courses import router as courses_router

app = FastAPI(title="AI Trợ Giảng")

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(pedagogy_router)
app.include_router(eval_router)
app.include_router(courses_router)