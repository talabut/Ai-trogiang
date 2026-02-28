# backend/services/agent.py
from backend.agent.qa import QAAgent
from backend.agent.tools import check_knowledge_base
from backend.services.llm import generate_answer


class AgentService:
    def __init__(self):
        self.agent = QAAgent()

    def build_rag_prompt(self, question: str, evidences: list) -> str:
        """
        Build structured RAG prompt from retrieved evidences.
        """
        context_blocks = []

        for idx, ev in enumerate(evidences, start=1):
            metadata = ev.get("metadata", {})
            page = metadata.get("page", "N/A")
            content = ev.get("text", "")

            context_blocks.append(f"[{idx}] (page {page})\n{content}")

        context_text = "\n\n".join(context_blocks)

        prompt = (
            "You are a university teaching assistant.\n"
            "Answer strictly using ONLY the information provided in the CONTEXT section.\n"
            "Do NOT use outside knowledge.\n"
            "If the answer cannot be found in the context, respond exactly with: I don't know.\n\n"
            "CONTEXT:\n"
            f"{context_text}\n\n"
            "QUESTION:\n"
            f"{question}\n\n"
            "ANSWER:"
        )

        return prompt

    def chat(self, question: str, session_id: str, course_id: str):
        # 1️⃣ Retrieval
        tool_result = check_knowledge_base(question, course_id)

        # 2️⃣ Agent kiểm soát logic
        result = self.agent.answer(question, tool_result)

        evidences = result.get("evidences", [])

        # 🚫 Không có evidence → từ chối
        if not evidences:
            result["answer"] = "I don't know."
            return result

        # 🚫 Lọc evidence yếu
        valid_evidences = [
            ev for ev in evidences
            if ev.get("text") and len(ev.get("text").strip()) > 50
        ]

        if not valid_evidences:
            result["answer"] = "I don't know."
            return result

        # 3️⃣ Build grounded prompt
        rag_prompt = self.build_rag_prompt(
            question=question,
            evidences=valid_evidences
        )

        # 4️⃣ Single LLM call
        final_answer = generate_answer(rag_prompt)

        result["answer"] = final_answer
        result["confidence"] = 0.9
        result["reason"] = "GROUNDed_GENERATION"

        return result


agent_service = AgentService()