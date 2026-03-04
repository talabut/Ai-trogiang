import logging
import re
from typing import Dict, List, Optional

import numpy as np
from llama_index.core import Settings

from backend.agent.qa import QAAgent
from backend.agent.tools import check_knowledge_base
from backend.services.llm import generate_answer
from backend.services.query_expander import QueryExpander
from backend.services.query_rewriter import QueryRewriter
from backend.services.reranker import CrossEncoderReranker


logger = logging.getLogger(__name__)


class AgentService:
    MIN_EVIDENCE_LENGTH = 50
    MIN_EVIDENCE_COUNT = 1

    SIMILARITY_THRESHOLD = 0.5
    MIN_COVERAGE_RATIO = 0.7
    CONCEPT_SIMILARITY_THRESHOLD = 0.35
    CONCEPT_MIN_COVERAGE_RATIO = 0.4

    OUT_OF_SCOPE_MAX_SCORE = 0.15
    OUT_OF_SCOPE_MIN_TOKEN_OVERLAP = 0.05

    REFUSAL_MESSAGES = {
        "NO_MATCH": "Tài liệu không đề cập trực tiếp nội dung câu hỏi.",
        "WEAK_EVIDENCE": "Tài liệu có đề cập gián tiếp nhưng không đủ bằng chứng học thuật để trả lời.",
        "OUT_OF_SCOPE": "Câu hỏi nằm ngoài phạm vi nội dung tài liệu đã nạp.",
    }

    QUESTION_TYPE_DOCUMENT = "DOCUMENT"
    QUESTION_TYPE_CONCEPT = "CONCEPT"
    QUESTION_TYPE_FACT = "FACT"

    def __init__(self):
        self.agent = QAAgent()
        self.embedding_model = Settings.embed_model
        self.reranker = CrossEncoderReranker()
        self.rewriter = QueryRewriter()
        self.expander = QueryExpander()

    def _resolve_target_language(self, question: str) -> str:
        q_lower = question.lower()

        if "trả lời bằng tiếng anh" in q_lower or "answer in english" in q_lower:
            return "English"

        if "trả lời bằng tiếng việt" in q_lower or "answer in vietnamese" in q_lower:
            return "Vietnamese"

        vietnamese_chars = "ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"

        if any(c in q_lower for c in vietnamese_chars):
            return "Vietnamese"

        return "English"

    def build_rag_prompt(self, question: str, evidences: list, target_language: str) -> str:
        context_blocks = []

        for idx, ev in enumerate(evidences, start=1):
            metadata = ev.get("metadata", {})
            page = metadata.get("page", "N/A")
            content = ev.get("text", "")
            context_blocks.append(f"[{idx}] (page {page})\n{content}")

        context_text = "\n\n".join(context_blocks)

        prompt = (
            "You are a university teaching assistant.\n"
            f"You MUST answer in {target_language}.\n"
            "Answer strictly using ONLY the information provided in the CONTEXT section.\n"
            "Do NOT use outside knowledge.\n"
            "Every factual statement MUST include citation in format [number].\n"
            "If the answer cannot be found in the context, do not fabricate.\n\n"
            "CONTEXT:\n"
            f"{context_text}\n\n"
            "QUESTION:\n"
            f"{question}\n\n"
            "ANSWER:"
        )

        return prompt

    def build_document_prompt(self, question: str, evidences: list, target_language: str) -> str:
        context_blocks = []
        for idx, ev in enumerate(evidences, start=1):
            metadata = ev.get("metadata", {})
            page = metadata.get("page", "N/A")
            content = ev.get("text", "")
            context_blocks.append(f"[{idx}] (page {page})\n{content}")

        context_text = "\n\n".join(context_blocks)
        return (
            "You are a university teaching assistant.\n"
            f"You MUST answer in {target_language}.\n"
            "Task: summarize document-level information only.\n"
            "Use ONLY the provided CONTEXT. Do NOT use outside knowledge.\n"
            "If context is insufficient, state that clearly.\n\n"
            f"CONTEXT:\n{context_text}\n\n"
            f"QUESTION:\n{question}\n\n"
            "ANSWER:"
        )

    def build_concept_prompt(self, question: str, evidences: list, target_language: str) -> str:
        context_blocks = []
        for idx, ev in enumerate(evidences, start=1):
            metadata = ev.get("metadata", {})
            page = metadata.get("page", "N/A")
            content = ev.get("text", "")
            context_blocks.append(f"[{idx}] (page {page})\n{content}")

        context_text = "\n\n".join(context_blocks)
        return (
            "You are a university teaching assistant.\n"
            f"You MUST answer in {target_language}.\n"
            "Answer concept/section-level only from CONTEXT.\n"
            "Do NOT use outside knowledge.\n"
            "If unsure, state insufficient evidence.\n\n"
            f"CONTEXT:\n{context_text}\n\n"
            f"QUESTION:\n{question}\n\n"
            "ANSWER:"
        )

    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

    def _split_sentences(self, text: str):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def _validate_grounding_with_thresholds(
        self,
        answer: str,
        evidences: list,
        similarity_threshold: float,
        min_coverage_ratio: float,
    ):
        sentences = self._split_sentences(answer)
        if not sentences:
            return False, 0.0

        evidence_texts = [ev["text"] for ev in evidences]
        evidence_vectors = [
            self.embedding_model.get_text_embedding(text)
            for text in evidence_texts
        ]

        supported_count = 0

        for sentence in sentences:
            sentence_vec = self.embedding_model.get_text_embedding(sentence)

            similarities = [
                self._cosine_similarity(sentence_vec, ev_vec)
                for ev_vec in evidence_vectors
            ]

            max_sim = max(similarities) if similarities else 0

            if max_sim >= similarity_threshold:
                supported_count += 1

        coverage_ratio = supported_count / len(sentences)

        if coverage_ratio >= min_coverage_ratio:
            return True, coverage_ratio

        return False, coverage_ratio

    def _validate_grounding(self, answer: str, evidences: list):
        return self._validate_grounding_with_thresholds(
            answer=answer,
            evidences=evidences,
            similarity_threshold=self.SIMILARITY_THRESHOLD,
            min_coverage_ratio=self.MIN_COVERAGE_RATIO,
        )

    def _validate_citations(self, answer: str, evidences: list):
        citation_numbers = re.findall(r"\[(\d+)\]", answer)

        if not citation_numbers:
            return False, "NO_CITATION"

        max_index = len(evidences)

        for num in citation_numbers:
            idx = int(num)
            if idx < 1 or idx > max_index:
                return False, "INVALID_CITATION_INDEX"

        return True, "VALID_CITATION"

    def _unique_merge(self, evidences_1: List[Dict], evidences_2: List[Dict]) -> List[Dict]:
        combined = evidences_1 + evidences_2
        seen = set()
        merged = []
        for ev in combined:
            key = (ev.get("text") or "")[:200]
            if key and key not in seen:
                merged.append(ev)
                seen.add(key)
        return merged

    def _get_retrieval_stats(self, evidences: List[Dict]) -> Dict[str, float]:
        max_score = max(
            (ev.get("score") for ev in evidences if ev.get("score") is not None),
            default=0.0,
        )
        return {
            "nodes_found": len(evidences),
            "max_score": float(max_score),
        }

    def _extract_question_tokens(self, question: str) -> List[str]:
        tokens = re.findall(r"\w+", question.lower())
        return [t for t in tokens if len(t) >= 4]

    def _classify_question_type(self, question: str) -> str:
        q = question.lower()

        fact_markers = [
            "chứng minh",
            "prove",
            "so sánh",
            "compare",
            "better than",
            "tốt hơn",
            "hiệu năng",
            "performance",
            "accuracy",
            "f1",
            "benchmark",
            "trade-off",
        ]
        if any(marker in q for marker in fact_markers):
            return self.QUESTION_TYPE_FACT

        document_markers = [
            "tài liệu này",
            "báo cáo này",
            "đề tài gì",
            "đề tài chính",
            "mấy chương",
            "chương",
            "tổng quan",
            "overview",
            "this document",
            "this report",
            "main topic",
            "how many chapters",
        ]
        if any(marker in q for marker in document_markers):
            return self.QUESTION_TYPE_DOCUMENT

        return self.QUESTION_TYPE_CONCEPT

    def _is_out_of_scope(self, question: str, evidences: List[Dict]) -> bool:
        if not evidences:
            return False

        stats = self._get_retrieval_stats(evidences)
        question_tokens = self._extract_question_tokens(question)
        if not question_tokens:
            return False

        evidence_text = " ".join((ev.get("text") or "")[:600].lower() for ev in evidences[:5])
        overlap = sum(1 for token in question_tokens if token in evidence_text)
        overlap_ratio = overlap / len(question_tokens)

        return (
            stats["max_score"] <= self.OUT_OF_SCOPE_MAX_SCORE
            and overlap_ratio < self.OUT_OF_SCOPE_MIN_TOKEN_OVERLAP
        )

    def _decide_refusal_reason(self, question: str, evidences: List[Dict], default_reason: str) -> str:
        if not evidences:
            return "NO_MATCH"
        if self._is_out_of_scope(question, evidences):
            return "OUT_OF_SCOPE"
        return default_reason

    def _build_refusal(self, reason: str, evidences: List[Dict], sources: Optional[List[str]] = None):
        stats = self._get_retrieval_stats(evidences)
        message = self.REFUSAL_MESSAGES.get(reason, self.REFUSAL_MESSAGES["WEAK_EVIDENCE"])
        logger.info(
            f"[RAG] decision={reason} | nodes_found={stats['nodes_found']} | max_score={stats['max_score']}"
        )
        return {
            "answer": None,
            "reason": reason,
            "message": message,
            "retrieval_stats": stats,
            "evidences": evidences,
            "sources": sources or [],
        }

    def chat(self, question: str, session_id: str, course_id: str):
        del session_id

        target_language = self._resolve_target_language(question)
        question_type = self._classify_question_type(question)
        rewritten_question = self.rewriter.rewrite(question)
        logger.info(f"[RAG] question_type={question_type}")

        tool_result_1 = check_knowledge_base(rewritten_question, course_id)
        result_1 = self.agent.answer(rewritten_question, tool_result_1)
        evidences_1 = result_1.get("evidences", [])

        if not evidences_1:
            return self._build_refusal("NO_MATCH", [], [])

        expanded_query = self.expander.expand(rewritten_question, evidences_1)

        tool_result_2 = check_knowledge_base(expanded_query, course_id)
        result_2 = self.agent.answer(expanded_query, tool_result_2)
        evidences_2 = result_2.get("evidences", [])

        evidences = self._unique_merge(evidences_1, evidences_2)
        if not evidences:
            return self._build_refusal("NO_MATCH", [], [])

        logger.info(f"[RAG] merged_nodes={len(evidences)}")

        valid_evidences = []
        for idx, ev in enumerate(evidences, start=1):
            text = (ev.get("text") or "").strip()
            score = ev.get("score")

            if not text:
                logger.info(f"[RAG] node_{idx} score={score} reason=EMPTY_TEXT")
                continue

            if question_type != self.QUESTION_TYPE_DOCUMENT and len(text) < self.MIN_EVIDENCE_LENGTH:
                logger.info(f"[RAG] node_{idx} score={score} reason=SHORT_TEXT")
                continue

            logger.info(f"[RAG] node_{idx} score={score} reason=KEEP")
            valid_evidences.append(ev)

        if len(valid_evidences) < self.MIN_EVIDENCE_COUNT:
            reason = self._decide_refusal_reason(question, evidences, "WEAK_EVIDENCE")
            return self._build_refusal(reason, evidences, result_1.get("sources", []))

        if len(valid_evidences) >= 6:
            reranked_evidences = self.reranker.rerank(
                rewritten_question,
                valid_evidences,
                top_n=5,
            )
        else:
            reranked_evidences = valid_evidences[:5]

        if not reranked_evidences:
            reason = self._decide_refusal_reason(question, valid_evidences, "WEAK_EVIDENCE")
            return self._build_refusal(reason, valid_evidences, result_1.get("sources", []))

        if question_type == self.QUESTION_TYPE_DOCUMENT:
            prompt = self.build_document_prompt(
                question=question,
                evidences=reranked_evidences,
                target_language=target_language,
            )
        elif question_type == self.QUESTION_TYPE_CONCEPT:
            prompt = self.build_concept_prompt(
                question=question,
                evidences=reranked_evidences,
                target_language=target_language,
            )
        else:
            prompt = self.build_rag_prompt(
                question=question,
                evidences=reranked_evidences,
                target_language=target_language,
            )

        final_answer = generate_answer(prompt)

        if not final_answer or not final_answer.strip():
            reason = self._decide_refusal_reason(question, reranked_evidences, "WEAK_EVIDENCE")
            return self._build_refusal(reason, reranked_evidences, result_1.get("sources", []))

        if question_type == self.QUESTION_TYPE_FACT:
            is_grounded, coverage_ratio = self._validate_grounding(
                final_answer,
                reranked_evidences,
            )
            if not is_grounded:
                reason = self._decide_refusal_reason(question, reranked_evidences, "WEAK_EVIDENCE")
                return self._build_refusal(reason, reranked_evidences, result_1.get("sources", []))

            citation_ok, _citation_reason = self._validate_citations(
                final_answer,
                reranked_evidences,
            )
            if not citation_ok:
                reason = self._decide_refusal_reason(question, reranked_evidences, "WEAK_EVIDENCE")
                return self._build_refusal(reason, reranked_evidences, result_1.get("sources", []))
        elif question_type == self.QUESTION_TYPE_CONCEPT:
            is_grounded, coverage_ratio = self._validate_grounding_with_thresholds(
                answer=final_answer,
                evidences=reranked_evidences,
                similarity_threshold=self.CONCEPT_SIMILARITY_THRESHOLD,
                min_coverage_ratio=self.CONCEPT_MIN_COVERAGE_RATIO,
            )
            if not is_grounded:
                reason = self._decide_refusal_reason(question, reranked_evidences, "WEAK_EVIDENCE")
                return self._build_refusal(reason, reranked_evidences, result_1.get("sources", []))
        else:
            # Document-level questions: no strict sentence-level grounding/citation gate.
            coverage_ratio = None

        evidence_count = len(reranked_evidences)
        similarity_scores = [
            ev.get("score", 0.5)
            for ev in reranked_evidences
            if ev.get("score") is not None
        ]

        avg_score = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        avg_score = max(0.0, min(avg_score, 1.0))

        if coverage_ratio is None:
            confidence = (
                0.5 * min(evidence_count / 5, 1.0)
                + 0.5 * min(avg_score, 1.0)
            )
        else:
            confidence = (
                0.4 * coverage_ratio
                + 0.3 * min(evidence_count / 5, 1.0)
                + 0.3 * min(avg_score, 1.0)
            )

        return {
            "answer": final_answer.strip(),
            "confidence": round(min(confidence, 0.95), 3),
            "coverage_ratio": coverage_ratio,
            "reason": "GROUNDED_WITH_CITATION",
            "retrieval_stats": self._get_retrieval_stats(reranked_evidences),
            "evidences": reranked_evidences,
            "sources": result_1.get("sources", []),
        }


agent_service = AgentService()
