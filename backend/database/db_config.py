import sqlite3
from pathlib import Path

DB_PATH = Path("data/app_database.db")

def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Để truy xuất theo tên cột
    return conn

def init_db():
    conn = get_db_connection()
    # Tạo bảng khóa học và bảng người dùng nếu chưa có
    conn.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()