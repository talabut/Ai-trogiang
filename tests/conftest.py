# conftest.py
import sys
import os
import shutil
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from main import app

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
# =========================
# 🔒 LỚP 2: ÉP TEST MODE
# =========================
@pytest.fixture(scope="session", autouse=True)
def force_test_env():
    os.environ["APP_ENV"] = "test"
    os.environ["INDEX_ROOT"] = "data/_test_indexes"
    os.environ["DISABLE_PERSIST"] = "1"
    yield


# =========================
# 🧹 LỚP 1: RESET INDEX STATE
# =========================
TEST_INDEX_ROOT = Path("data/_test_indexes")

@pytest.fixture(scope="function", autouse=False)
def reset_test_indexes():
    if TEST_INDEX_ROOT.exists():
        shutil.rmtree(TEST_INDEX_ROOT)

    TEST_INDEX_ROOT.mkdir(parents=True, exist_ok=True)

    yield

    shutil.rmtree(TEST_INDEX_ROOT, ignore_errors=True)


# =========================
# 🌐 API CLIENT
# =========================
@pytest.fixture(scope="function")
def client():
    # reset rate-limit state trước mỗi test
    if hasattr(app.state, "RATE"):
        app.state.RATE.clear()

    return TestClient(app)
