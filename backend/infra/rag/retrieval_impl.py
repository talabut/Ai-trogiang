from typing import List, Dict, Optional
from backend.core.interfaces import IRetriever
from backend.config.integrity_config import settings
from backend.utils.memory_guard import enforce_memory_budget
from backend.vectorstore.faiss_store import load_index

class FaissRetriever(IRetriever):
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict]:

        enforce_memory_budget()

        index = load_index()
        # giả định embedding đã có
        query_vector = self._embed(query)

        scores, ids = index.search(query_vector, top_k)
        th = threshold if threshold is not None else settings.RETRIEVAL_THRESHOLD

        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            if score < th:
                continue
            results.append({
                "content": f"DOC_{idx}",
                "score": float(score),
                "metadata": {"source": "faiss"}
            })

        return results

    def _embed(self, q: str):
        import numpy as np
        return np.random.rand(1, 768).astype("float32")
