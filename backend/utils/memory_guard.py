import psutil
from fastapi import HTTPException
from backend.config.integrity_config import settings

def enforce_memory_budget():
    vm = psutil.virtual_memory()
    used_mb = (vm.total - vm.available) / (1024 * 1024)
    if used_mb > settings.MAX_MEMORY_MB:
        raise HTTPException(
            status_code=503,
            detail="Memory pressure too high, try later"
        )
