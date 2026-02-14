# backend/security/guard.py
import builtins
import os
import subprocess


class RuntimeSandboxError(RuntimeError):
    pass


_original_open = builtins.open


def enable_runtime_sandbox():
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
    data_root = os.path.abspath("backend/data")

    def sandboxed_open(file, mode="r", *args, **kwargs):
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            abs_path = os.path.abspath(file)
            if not abs_path.startswith(data_root):
                raise RuntimeSandboxError("Runtime sandbox violation")
        return _original_open(file, mode, *args, **kwargs)

    builtins.open = sandboxed_open
