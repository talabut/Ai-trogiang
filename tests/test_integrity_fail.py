import os
import pytest
from backend.bootstrap import bootstrap_system
from backend.config.integrity_config import settings

def test_fail_when_index_not_writable(monkeypatch):
    monkeypatch.setattr(settings, "FAISS_INDEX_DIR", "/root/forbidden")
    with pytest.raises(SystemExit):
        bootstrap_system()
