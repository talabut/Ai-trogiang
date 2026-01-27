from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import courses, auth

app = FastAPI(title="AI Pedagogy Assistant API")

# FIX: Cấu hình CORS
# Cho phép Frontend (Vite/React) truy cập vào API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000", # Nếu bạn dùng Next.js hoặc port khác
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Cho phép tất cả các phương thức GET, POST, PUT, DELETE...
    allow_headers=["*"], # Cho phép tất cả các headers
)

# Đăng ký các router
app.include_router(auth.router)
app.include_router(courses.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Hệ thống hỗ trợ giảng dạy AI đã sẵn sàng"
    }