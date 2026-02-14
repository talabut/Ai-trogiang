# tests/test_integrity_fail.py
import pytest
from backend.bootstrap import bootstrap_system
from backend.config.integrity_config import settings

def test_fail_when_index_not_writable(monkeypatch):
    # Set path hợp lệ
    monkeypatch.setattr(settings, "FAISS_INDEX_DIR", "dummy_path")

    # Mock đúng tầng integrity
    def fake_assert_dir_writable(path):
        if path == "dummy_path":
            raise SystemExit("FAISS index dir not writable")

    monkeypatch.setattr(
        "backend.config.integrity_config.assert_dir_writable",
        fake_assert_dir_writable
    )

    with pytest.raises(SystemExit):
        bootstrap_system()
