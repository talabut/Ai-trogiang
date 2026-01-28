import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import upload, chat, courses
from backend.database.db_config import init_db

app = FastAPI(title="AI Teaching Assistant System - No Auth Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Router (Đã bỏ auth)
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["AI Chat"])

@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 Hệ thống đã sẵn sàng (CHẾ ĐỘ KHÔNG LOGIN)!")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)