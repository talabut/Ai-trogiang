from backend.config.integrity_config import DISABLE_GUARD

import builtins
import os
import subprocess
from backend.config.integrity_config import settings


class RuntimeSandboxError(RuntimeError):
    pass


_original_open = builtins.open


def enable_runtime_sandbox():
    if DISABLE_GUARD:
        return  # bypass toàn bộ sandbox    
    def _blocked(*args, **kwargs):
        raise RuntimeSandboxError("Runtime sandbox violation")

    # --- Dangerous execution ---
    builtins.eval = _blocked
    builtins.exec = _blocked

    # --- OS / Process execution ---
    os.system = _blocked
    subprocess.run = _blocked
    subprocess.Popen = _blocked

    # --- Filesystem isolation ---
    data_root = os.path.abspath(settings.DATA_DIR)

    def sandboxed_open(file, mode="r", *args, **kwargs):
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            abs_path = os.path.abspath(file)
            if not abs_path.startswith(data_root):
                raise RuntimeSandboxError(
                    f"Write blocked outside sandbox: {abs_path}"
                )
        return _original_open(file, mode, *args, **kwargs)

    builtins.open = sandboxed_open
