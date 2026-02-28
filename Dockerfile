# Sử dụng Python 3.10 slim để nhẹ nhất (Paddle/Torch ổn định nhất trên 3.10)
FROM python:3.10-slim

WORKDIR /app

# 1. Cài đặt System Dependencies (Cần cho OpenCV và PaddleOCR)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Cài đặt Python Dependencies
# Tách riêng bước này để tận dụng Docker Cache
COPY requirements.txt .

# Mẹo: Cài Torch CPU riêng trước để giảm dung lượng image (nếu không dùng GPU)
RUN pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy Source Code
COPY . .

# 4. Tạo thư mục data và cấp quyền (Tránh lỗi PermissionError trong code)
RUN mkdir -p /app/data/faiss_index /app/data/raw_docs /app/data/bm25 \
    && chmod -R 777 /app/data

# 5. Environment Variables mặc định
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DISABLE_GUARD=false

# 6. Healthcheck & Entrypoint
EXPOSE 8000

# Script khởi động: Chạy migrate/bootstrap trước nếu cần, sau đó start app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]