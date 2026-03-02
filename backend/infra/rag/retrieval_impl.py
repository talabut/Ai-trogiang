#backend/infra/rag/retrieval_impl.py
import logging
import json
from typing import List
from pathlib import Path

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.retrievers.bm25 import BM25Retriever
import backend.infra.rag.llama_settings

from backend.rag.llama_ingest import get_index_path, INDEX_VERSION, EMBEDDING_MODEL_TAG


logger = logging.getLogger(__name__)


class LlamaRetriever:
    """
    Retrieval layer cho RAG system.
    - Luôn trả top_k (3–5)
    - Không dùng threshold cứng
    - Fail fast nếu index meta mismatch
    """

    def __init__(self, course_id: str, top_k: int = 5):
        if top_k < 3:
            top_k = 3
        if top_k > 5:
            top_k = 5

        self.course_id = course_id
        self.top_k = top_k

        index_path = Path(get_index_path(course_id))

        if not index_path.exists():
            raise ValueError(
                f"[Retrieval] Index path không tồn tại cho course_id={course_id}: {index_path}"
            )

        # =========================
        # 🔥 VALIDATE INDEX META
        # =========================

        meta_path = index_path / "index_meta.json"

        if not meta_path.exists():
            raise RuntimeError(
                f"[Retrieval] index_meta.json missing for course_id={course_id}"
            )

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            raise RuntimeError(
                f"[Retrieval] index_meta.json corrupted for course_id={course_id}"
            )

        if meta.get("index_version") != INDEX_VERSION:
            raise RuntimeError(
                f"[Retrieval] INDEX_VERSION mismatch. "
                f"Expected={INDEX_VERSION} | Found={meta.get('index_version')}"
            )

        if meta.get("embedding_model_tag") != EMBEDDING_MODEL_TAG:
            raise RuntimeError(
                f"[Retrieval] EMBEDDING_MODEL mismatch. "
                f"Expected={EMBEDDING_MODEL_TAG} | Found={meta.get('embedding_model_tag')}"
            )

        # =========================
        # LOAD STORAGE
        # =========================

        storage_context = StorageContext.from_defaults(
            persist_dir=str(index_path)
        )

        self.index: VectorStoreIndex = load_index_from_storage(storage_context)

        self.retriever = self.index.as_retriever(
            similarity_top_k=self.top_k
        )
        
        # 🔥 BM25 Retriever (keyword)
        self.bm25_retriever = BM25Retriever.from_defaults(
            docstore=self.index.docstore,
            similarity_top_k=self.top_k
        )

        logger.info(
            f"[Retrieval] Loaded index | "
            f"course_id={course_id} | top_k={self.top_k} | "
            f"version={INDEX_VERSION}"
        )

    def retrieve(self, query: str) -> List[NodeWithScore]:

        logger.info(
            f"[Hybrid Retrieval] Query='{query}' | course_id={self.course_id}"
        )

        # === Dense ===
        dense_nodes: List[NodeWithScore] = self.retriever.retrieve(query)

        # === BM25 ===
        bm25_nodes: List[NodeWithScore] = self.bm25_retriever.retrieve(query)

        # === Merge (deduplicate by node_id) ===
        combined = dense_nodes + bm25_nodes

        seen = set()
        merged_nodes = []

        for node in combined:
            node_id = node.node.node_id
            if node_id not in seen:
                merged_nodes.append(node)
                seen.add(node_id)

        if not merged_nodes:
            logger.warning(
                f"[Hybrid Retrieval] EMPTY RESULT | course_id={self.course_id}"
            )
            return []

        # Log preview
        for i, node in enumerate(merged_nodes[:5]):
            score = node.score
            text_preview = node.node.get_content()[:200].replace("\n", " ")

            logger.info(
                f"[Hybrid] Rank={i+1} | Score={score} | Preview='{text_preview}'"
            )

        return merged_nodes[: self.top_k * 2]  # return extra, reranker sẽ lọc
def retrieve(
    query: str,
    course_id: str,
    top_k: int = 5
) -> List[NodeWithScore]:
    """
    Canonical retrieval entry-point cho Agent layer.
    Agent KHÔNG được khởi tạo retriever trực tiếp.
    """
    retriever = LlamaRetriever(course_id=course_id, top_k=top_k)
    return retriever.retrieve(query)