import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import các router
from backend.api import auth, upload, chat, courses
from backend.database.db_config import init_db

app = FastAPI(title="AI Teaching Assistant System")

# Cấu hình CORS để Frontend (Port 5173) gọi được Backend (Port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên đổi thành ["http://localhost:5173"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["AI Chat"])

# Mount thư mục upload để có thể truy cập file nếu cần (Optional)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
# app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 Hệ thống AI Trợ giảng đã sẵn sàng!")
    print("👉 Swagger UI: http://localhost:8000/docs")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)