import re
import numpy as np

from backend.agent.qa import QAAgent
from backend.agent.tools import check_knowledge_base
from backend.services.llm import generate_answer
from backend.services.reranker import CrossEncoderReranker
from backend.services.query_rewriter import QueryRewriter
from backend.services.query_expander import QueryExpander

from llama_index.core import Settings


class AgentService:
    MIN_EVIDENCE_LENGTH = 50
    MIN_EVIDENCE_COUNT = 1
    SAFE_FALLBACK_MESSAGE = "I don't know."

    # Grounding config
    SIMILARITY_THRESHOLD = 0.5
    MIN_COVERAGE_RATIO = 0.7

    def __init__(self):
        self.agent = QAAgent()
        self.embedding_model = Settings.embed_model
        self.reranker = CrossEncoderReranker()
        self.rewriter = QueryRewriter()
        self.expander = QueryExpander()

    # =========================================================
    # LANGUAGE RESOLUTION
    # =========================================================
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

    # =========================================================
    # GENERAL FALLBACK (Mode 3)
    # =========================================================
    def _generate_general_answer(self, question: str, target_language: str) -> str:
        prompt = (
            "You are a helpful university teaching assistant.\n"
            f"You MUST answer in {target_language}.\n\n"
            f"QUESTION:\n{question}\n\n"
            "ANSWER:"
        )

        answer = generate_answer(prompt)
        return answer.strip() if answer else self.SAFE_FALLBACK_MESSAGE

    # =========================================================
    # RAG PROMPT
    # =========================================================
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
            "If the answer cannot be found in the context, respond accordingly.\n\n"
            "CONTEXT:\n"
            f"{context_text}\n\n"
            "QUESTION:\n"
            f"{question}\n\n"
            "ANSWER:"
        )

        return prompt

    # =========================================================
    # GROUNDING
    # =========================================================
    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

    def _split_sentences(self, text: str):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def _validate_grounding(self, answer: str, evidences: list):
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

            if max_sim >= self.SIMILARITY_THRESHOLD:
                supported_count += 1

        coverage_ratio = supported_count / len(sentences)

        if coverage_ratio >= self.MIN_COVERAGE_RATIO:
            return True, coverage_ratio

        return False, coverage_ratio

    # =========================================================
    # CITATION VALIDATION
    # =========================================================
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

    # =========================================================
    # CHAT ENTRY (MODE 3)
    # =========================================================
    def chat(self, question: str, session_id: str, course_id: str):

        target_language = self._resolve_target_language(question)

        rewritten_question = self.rewriter.rewrite(question)

        # ---------- Retrieval 1 ----------
        tool_result_1 = check_knowledge_base(rewritten_question, course_id)
        result_1 = self.agent.answer(rewritten_question, tool_result_1)
        evidences_1 = result_1.get("evidences", [])

        if not evidences_1:
            general_answer = self._generate_general_answer(question, target_language)
            return {
                "answer": general_answer,
                "confidence": 0.3,
                "reason": "NO_EVIDENCE_GENERAL_FALLBACK",
                "evidences": []
            }

        # ---------- Query Expansion ----------
        expanded_query = self.expander.expand(rewritten_question, evidences_1)

        # ---------- Retrieval 2 ----------
        tool_result_2 = check_knowledge_base(expanded_query, course_id)
        result_2 = self.agent.answer(expanded_query, tool_result_2)
        evidences_2 = result_2.get("evidences", [])

        combined = evidences_1 + evidences_2

        seen = set()
        merged_evidences = []
        for ev in combined:
            key = ev["text"][:200]
            if key not in seen:
                merged_evidences.append(ev)
                seen.add(key)

        evidences = merged_evidences

        if not evidences:
            general_answer = self._generate_general_answer(question, target_language)
            return {
                "answer": general_answer,
                "confidence": 0.3,
                "reason": "NO_EVIDENCE_AFTER_MERGE",
                "evidences": []
            }

        valid_evidences = [
            ev for ev in evidences
            if ev.get("text") and len(ev.get("text").strip()) >= self.MIN_EVIDENCE_LENGTH
        ]

        if len(valid_evidences) < self.MIN_EVIDENCE_COUNT:
            general_answer = self._generate_general_answer(question, target_language)
            return {
                "answer": general_answer,
                "confidence": 0.3,
                "reason": "LOW_QUALITY_EVIDENCE_GENERAL",
                "evidences": []
            }

        # ---------- Rerank ----------
        if len(valid_evidences) >= 6:
            reranked_evidences = self.reranker.rerank(
                rewritten_question,
                valid_evidences,
                top_n=5
            )
        else:
            reranked_evidences = valid_evidences[:5]

        if not reranked_evidences:
            general_answer = self._generate_general_answer(question, target_language)
            return {
                "answer": general_answer,
                "confidence": 0.3,
                "reason": "RERANK_EMPTY_GENERAL",
                "evidences": []
            }

        # ---------- RAG ----------
        rag_prompt = self.build_rag_prompt(
            question=question,
            evidences=reranked_evidences,
            target_language=target_language
        )

        final_answer = generate_answer(rag_prompt)

        if not final_answer or not final_answer.strip():
            general_answer = self._generate_general_answer(question, target_language)
            return {
                "answer": general_answer,
                "confidence": 0.3,
                "reason": "EMPTY_LLM_GENERAL",
                "evidences": reranked_evidences
            }

        # ---------- Grounding ----------
        is_grounded, coverage_ratio = self._validate_grounding(
            final_answer,
            reranked_evidences
        )

        if not is_grounded:
            general_answer = self._generate_general_answer(question, target_language)

            if target_language == "Vietnamese":
                prefix = "Tôi không tìm thấy thông tin đủ rõ ràng trong tài liệu được cung cấp.\n\nTheo kiến thức chung:\n"
            else:
                prefix = "I could not find sufficient grounded information in the provided documents.\n\nBased on general knowledge:\n"

            return {
                "answer": prefix + general_answer,
                "confidence": 0.4,
                "coverage_ratio": coverage_ratio,
                "reason": "NOT_GROUNDED_GENERAL_EXPLANATION",
                "evidences": reranked_evidences
            }

        # ---------- Citation ----------
        citation_ok, citation_reason = self._validate_citations(
            final_answer,
            reranked_evidences
        )

        if not citation_ok:
            general_answer = self._generate_general_answer(question, target_language)

            if target_language == "Vietnamese":
                prefix = "Câu trả lời không thể trích dẫn rõ ràng từ tài liệu.\n\nTheo kiến thức chung:\n"
            else:
                prefix = "The answer could not be properly cited from the documents.\n\nBased on general knowledge:\n"

            return {
                "answer": prefix + general_answer,
                "confidence": 0.4,
                "reason": citation_reason,
                "evidences": reranked_evidences
            }

        # ---------- Confidence ----------
        evidence_count = len(reranked_evidences)
        similarity_scores = [
            ev.get("score", 0.5)
            for ev in reranked_evidences
            if ev.get("score") is not None
        ]

        avg_score = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        avg_score = max(0.0, min(avg_score, 1.0))

        confidence = (
            0.4 * coverage_ratio +
            0.3 * min(evidence_count / 5, 1.0) +
            0.3 * min(avg_score, 1.0)
        )

        return {
            "answer": final_answer.strip(),
            "confidence": round(min(confidence, 0.95), 3),
            "coverage_ratio": coverage_ratio,
            "reason": "GROUNDED_WITH_CITATION",
            "evidences": reranked_evidences
        }


agent_service = AgentService()