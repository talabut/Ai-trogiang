import logging
import json
from typing import List
from pathlib import Path

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.schema import NodeWithScore

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

        logger.info(
            f"[Retrieval] Loaded index | "
            f"course_id={course_id} | top_k={self.top_k} | "
            f"version={INDEX_VERSION}"
        )

    def retrieve(self, query: str) -> List[NodeWithScore]:
        """
        Retrieve top_k nodes và log score để debug recall.
        """
        logger.info(
            f"[Retrieval] Query='{query}' | course_id={self.course_id} | top_k={self.top_k}"
        )

        nodes: List[NodeWithScore] = self.retriever.retrieve(query)

        if not nodes:
            logger.warning(
                f"[Retrieval] EMPTY RESULT | course_id={self.course_id}"
            )
            return []

        # 🔴 Log score + preview nội dung
        for i, node in enumerate(nodes):
            score = node.score
            text_preview = node.node.get_content()[:200].replace("\n", " ")

            logger.info(
                f"[Retrieval] Rank={i+1} | Score={score:.4f} | Preview='{text_preview}'"
            )

        return nodes
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