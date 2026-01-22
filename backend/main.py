from fastapi import FastAPI
from backend.api.chat import router as chat_router
from backend.api.upload import router as upload_router
from backend.api.exam import router as exam_router

app = FastAPI(title="AI Tro Giang")

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(exam_router, prefix="/exam", tags=["Exam"])

@app.get("/")
def health():
    return {"status": "ok", "message": "AI Tro Giang backend running"}
