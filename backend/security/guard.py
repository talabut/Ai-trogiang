import os
from fastapi import HTTPException

def safe_join(base: str, filename: str) -> str:
    fname = os.path.basename(filename)
    path = os.path.abspath(os.path.join(base, fname))

    if not path.startswith(os.path.abspath(base)):
        raise HTTPException(status_code=400, detail="Invalid path")

    return path
