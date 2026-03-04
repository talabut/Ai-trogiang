import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.retrievers.bm25 import BM25Retriever

import backend.infra.rag.llama_settings  # ensure Settings.embed_model is initialized
from backend.rag.llama_ingest import EMBEDDING_MODEL_TAG, INDEX_VERSION, get_index_path
from backend.services.llm import generate_answer

logger = logging.getLogger(__name__)


class QuizService:
    ACADEMIC_KEYWORDS = [
        "is defined as",
        "refers to",
        "is a",
        "defined as",
        "definition",
        "explains",
        "explanation",
        "method",
        "methodology",
        "approach",
        "procedure",
        "result",
        "finding",
        "according to",
        "in this study",
    ]

    def _load_nodes(self, course_id: str, query: str, top_k: int) -> List[NodeWithScore]:
        index_path = Path(get_index_path(course_id))
        if not index_path.exists():
            logger.warning("[RAG][QUIZ] decision=NO_MATCH reason=INDEX_NOT_FOUND")
            return []

        meta_path = index_path / "index_meta.json"
        if not meta_path.exists():
            logger.warning("[RAG][QUIZ] decision=NO_MATCH reason=INDEX_META_MISSING")
            return []

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if meta.get("index_version") != INDEX_VERSION:
            raise RuntimeError("[RAG][QUIZ] INDEX_VERSION_MISMATCH")
        if meta.get("embedding_model_tag") != EMBEDDING_MODEL_TAG:
            raise RuntimeError("[RAG][QUIZ] EMBEDDING_MODEL_MISMATCH")

        storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
        index: VectorStoreIndex = load_index_from_storage(storage_context)

        dense = index.as_retriever(similarity_top_k=top_k).retrieve(query)
        bm25 = BM25Retriever.from_defaults(docstore=index.docstore, similarity_top_k=top_k).retrieve(query)

        merged: List[NodeWithScore] = []
        seen = set()
        for node in dense + bm25:
            node_id = node.node.node_id
            if node_id not in seen:
                merged.append(node)
                seen.add(node_id)

        logger.info(f"[RAG][QUIZ] query=\"{query}\"")
        logger.info(f"[RAG][QUIZ] retrieved_nodes={len(merged)}")
        for i, node in enumerate(merged[:10], start=1):
            logger.info(f"[RAG][QUIZ] node_{i} score={node.score} reason=CANDIDATE")

        return merged

    def _topic_key(self, text: str) -> str:
        terms = re.findall(r"[A-Za-z0-9_]{4,}", text.lower())
        if not terms:
            return "misc"
        return " ".join(terms[:3])

    def _is_academically_sufficient(self, text: str) -> bool:
        normalized = (text or "").strip().lower()
        if len(normalized) < 150:
            return False
        return any(keyword in normalized for keyword in self.ACADEMIC_KEYWORDS)

    def _group_by_topic(self, nodes: List[NodeWithScore]) -> Dict[str, List[NodeWithScore]]:
        groups: Dict[str, List[NodeWithScore]] = {}
        for node in nodes:
            text = node.node.get_content() or ""
            key = self._topic_key(text)
            groups.setdefault(key, []).append(node)
        logger.info(f"[RAG][QUIZ] topic_groups={len(groups)}")
        return groups

    def _build_prompt(self, context: str) -> str:
        return (
            "You are generating one strict multiple-choice quiz question from academic context.\n"
            "ONLY use the provided context.\n"
            "Do NOT use outside knowledge.\n"
            "Do NOT infer facts not explicitly stated.\n"
            "Generate exactly one question with four options A/B/C/D and exactly one correct answer.\n"
            "Return only valid JSON with keys: question, options, correct_answer.\n"
            "options must be an object with keys A,B,C,D.\n\n"
            f"CONTEXT:\n{context}\n\n"
            "JSON:"
        )

    def _parse_quiz(self, raw: str) -> Optional[Dict[str, Any]]:
        raw = (raw or "").strip()
        if not raw:
            return None

        candidate = raw
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("{") and part.endswith("}"):
                    candidate = part
                    break
                if part.startswith("json"):
                    body = part[4:].strip()
                    if body.startswith("{") and body.endswith("}"):
                        candidate = body
                        break

        try:
            obj = json.loads(candidate)
        except Exception:
            return None

        if not isinstance(obj, dict):
            return None
        if "question" not in obj or "options" not in obj or "correct_answer" not in obj:
            return None

        options = obj.get("options")
        if not isinstance(options, dict):
            return None
        if set(options.keys()) != {"A", "B", "C", "D"}:
            return None

        answer = str(obj.get("correct_answer", "")).strip().upper()
        if answer not in {"A", "B", "C", "D"}:
            return None

        return {
            "question": str(obj["question"]).strip(),
            "options": {k: str(v).strip() for k, v in options.items()},
            "correct_answer": answer,
        }

    def generate_quiz(
        self,
        course_id: str,
        num_questions: int = 5,
        query: Optional[str] = None,
        top_k: int = 30,
    ) -> Dict[str, Any]:
        safe_top_k = max(20, min(top_k, 40))
        safe_n = max(1, min(num_questions, 20))
        retrieval_query = query or "main topics concepts definitions methods results conclusions"

        nodes = self._load_nodes(course_id=course_id, query=retrieval_query, top_k=safe_top_k)
        if not nodes:
            return {
                "success": False,
                "reason": "INSUFFICIENT_EVIDENCE",
                "detail": "Not enough academically sufficient chunks to generate quiz questions",
                "retrieval_stats": {"nodes_found": 0, "nodes_eligible": 0, "required": safe_n},
            }

        eligible_nodes: List[NodeWithScore] = []
        for node in nodes:
            text = node.node.get_content() or ""
            if self._is_academically_sufficient(text):
                eligible_nodes.append(node)
            else:
                logger.info(
                    f"[RAG][QUIZ] skip_node reason=INSUFFICIENT_ACADEMIC_CONTENT score={node.score}"
                )

        if len(eligible_nodes) < safe_n:
            logger.info(
                f"[RAG][QUIZ] decision=INSUFFICIENT_EVIDENCE required={safe_n} eligible={len(eligible_nodes)}"
            )
            return {
                "success": False,
                "reason": "INSUFFICIENT_EVIDENCE",
                "detail": "Not enough academically sufficient chunks to generate quiz questions",
                "retrieval_stats": {
                    "nodes_found": len(nodes),
                    "nodes_eligible": len(eligible_nodes),
                    "required": safe_n,
                },
            }

        groups = self._group_by_topic(eligible_nodes)
        selected: List[NodeWithScore] = []
        for topic_nodes in groups.values():
            if topic_nodes:
                selected.append(topic_nodes[0])
                if len(selected) >= safe_n:
                    break

        if len(selected) < safe_n:
            for node in eligible_nodes:
                if node not in selected:
                    selected.append(node)
                    if len(selected) >= safe_n:
                        break

        quizzes = []
        for node in selected[:safe_n]:
            text = node.node.get_content() or ""
            if len(text.strip()) < 80:
                logger.info(f"[RAG][QUIZ] skip_node score={node.score} reason=SHORT_CONTEXT")
                continue

            prompt = self._build_prompt(text[:1800])
            raw = generate_answer(prompt)
            parsed = self._parse_quiz(raw)
            if not parsed:
                logger.info("[RAG][QUIZ] skip_node reason=INVALID_MODEL_OUTPUT")
                continue

            parsed["evidence"] = {
                "chunk_id": node.node.node_id,
                "page": (node.node.metadata or {}).get("page", "N/A"),
            }
            quizzes.append(parsed)

        max_score = max((float(n.score) for n in nodes if n.score is not None), default=0.0)
        if not quizzes:
            logger.info("[RAG][QUIZ] decision=INSUFFICIENT_EVIDENCE")
            return {
                "success": False,
                "reason": "INSUFFICIENT_EVIDENCE",
                "detail": "Not enough academically sufficient chunks to generate quiz questions",
                "retrieval_stats": {
                    "nodes_found": len(nodes),
                    "nodes_eligible": len(eligible_nodes),
                    "required": safe_n,
                },
            }

        return {
            "success": True,
            "data": quizzes,
            "retrieval_stats": {"nodes_found": len(nodes), "max_score": max_score},
        }


quiz_service = QuizService()
