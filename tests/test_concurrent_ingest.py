import threading
from backend.rag.chunking import ingest_with_lock

results = []

def worker(text):
    res = ingest_with_lock(text, lambda t: None)
    results.append(res["status"])

def test_concurrent_ingest_dedup():
    threads = []
    for _ in range(3):
        t = threading.Thread(target=worker, args=("SAME_TEXT",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert results.count("ingested") == 1
    assert results.count("skipped") == 2
