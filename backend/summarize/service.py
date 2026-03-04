import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage

import backend.infra.rag.llama_settings  # ensure Settings.embed_model is initialized
from backend.rag.llama_ingest import EMBEDDING_MODEL_TAG, INDEX_VERSION, get_index_path
from backend.services.llm import generate_answer

logger = logging.getLogger(__name__)


class SummarizeService:
    def _load_all_nodes(self, course_id: str) -> List[Dict[str, Any]]:
        index_path = Path(get_index_path(course_id))
        if not index_path.exists():
            logger.warning("[RAG][SUMMARY] decision=NO_MATCH reason=INDEX_NOT_FOUND")
            return []

        meta_path = index_path / "index_meta.json"
        if not meta_path.exists():
            logger.warning("[RAG][SUMMARY] decision=NO_MATCH reason=INDEX_META_MISSING")
            return []

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if meta.get("index_version") != INDEX_VERSION:
            raise RuntimeError("[RAG][SUMMARY] INDEX_VERSION_MISMATCH")
        if meta.get("embedding_model_tag") != EMBEDDING_MODEL_TAG:
            raise RuntimeError("[RAG][SUMMARY] EMBEDDING_MODEL_MISMATCH")

        storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
        index: VectorStoreIndex = load_index_from_storage(storage_context)

        nodes = []
        # index.docstore.docs is expected mapping node_id -> TextNode
        for node_id, node in index.docstore.docs.items():
            text = node.get_content() if hasattr(node, "get_content") else ""
            metadata = getattr(node, "metadata", {}) or {}
            nodes.append({"chunk_id": node_id, "text": text, "metadata": metadata})

        logger.info(f"[RAG][SUMMARY] retrieved_nodes={len(nodes)}")
        return nodes

    def _section_key(self, page: int, summary_level: str) -> str:
        if summary_level == "outline":
            bucket = ((max(page, 1) - 1) // 3) * 3 + 1
            return f"Section pages {bucket}-{bucket + 2}"
        return f"Page {max(page, 1)}"

    def _chunk_prompt(self, text: str, summary_level: str) -> str:
        mode_instruction = (
            "Write concise outline points." if summary_level == "outline" else "Write lecture-note style concise factual notes."
        )
        return (
            "You are summarizing an academic document chunk.\n"
            "Summarize ONLY factual statements explicitly present in the chunk.\n"
            "Do NOT infer, speculate, or add external knowledge.\n"
            "Keep terminology unchanged from the chunk where possible.\n"
            f"{mode_instruction}\n"
            "Return plain text summary only.\n\n"
            f"CHUNK:\n{text}\n\n"
            "SUMMARY:"
        )

    def summarize(self, course_id: str, summary_level: str = "outline") -> Dict[str, Any]:
        if summary_level not in {"outline", "lecture_notes"}:
            return {
                "success": False,
                "reason": "INVALID_SUMMARY_LEVEL",
                "message": "summary_level must be 'outline' or 'lecture_notes'",
            }

        nodes = self._load_all_nodes(course_id)
        if not nodes:
            return {"success": False, "reason": "INSUFFICIENT_EVIDENCE"}

        sections: Dict[str, List[Dict[str, str]]] = {}
        kept_nodes = 0
        for node in nodes:
            text = (node.get("text") or "").strip()
            if len(text) < 80:
                logger.info("[RAG][SUMMARY] skip_node reason=SHORT_CONTEXT")
                continue

            page = int((node.get("metadata") or {}).get("page", 1) or 1)
            section = self._section_key(page=page, summary_level=summary_level)

            summary_text = generate_answer(self._chunk_prompt(text[:1800], summary_level=summary_level)).strip()
            if not summary_text:
                logger.info("[RAG][SUMMARY] skip_node reason=EMPTY_MODEL_OUTPUT")
                continue

            sections.setdefault(section, []).append({
                "text": summary_text,
                "source": f"page {page}",
            })
            kept_nodes += 1

        logger.info(f"[RAG][SUMMARY] kept_nodes={kept_nodes}")

        if not sections:
            logger.info("[RAG][SUMMARY] decision=INSUFFICIENT_EVIDENCE")
            return {"success": False, "reason": "INSUFFICIENT_EVIDENCE"}

        ordered = [{"section": k, "summary": v} for k, v in sorted(sections.items(), key=lambda x: x[0])]
        return {
            "success": True,
            "summary_level": summary_level,
            "data": ordered,
            "retrieval_stats": {"nodes_found": len(nodes), "nodes_used": kept_nodes},
        }


summarize_service = SummarizeService()
