# FILE: backend/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Chỉ import các api nghiệp vụ cơ bản
from backend.api import upload, chat

app = FastAPI(title="AI Teaching Assistant - NO AUTH MVP")

# Cấu hình CORS cho Frontend (Port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ĐĂNG KÝ ROUTER ---
# 1. Upload file (POST /upload/)
app.include_router(upload.router, prefix="/upload", tags=["Upload"])

# 2. Chat (POST /chat/query)
app.include_router(chat.router, prefix="/chat", tags=["AI Chat"])

@app.get("/")
def root():
    return {"message": "System is running (NO AUTH MODE)"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)