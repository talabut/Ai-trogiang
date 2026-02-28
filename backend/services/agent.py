from backend.agent.qa import QAAgent
from backend.agent.tools import check_knowledge_base
from backend.services.llm import generate_answer


class AgentService:
    def __init__(self):
        # Khởi tạo QAAgent để sử dụng cho các phương thức trong class
        self.agent = QAAgent()

    def build_rag_prompt(self, question: str, evidences: list) -> str:
        """
        Build structured RAG prompt from retrieved evidences.
        """
        context_blocks = []

        for idx, ev in enumerate(evidences, start=1):
            page = ev.get("page", "N/A")
            content = ev.get("content", "")
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
        # 1. Retrieval
        tool_result = check_knowledge_base(question, course_id)

        result = self.agent.answer(tool_result)

        # 2. Nếu có evidences → build prompt và gọi LLM
        evidences = result.get("evidences", [])

        # 🚫 Không có evidence → từ chối ngay
        if not evidences:
            result["answer"] = "I don't know."
            return result

        # 🚫 Lọc evidence yếu (content quá ngắn)
        valid_evidences = [
            ev for ev in evidences
            if ev.get("content") and len(ev.get("content").strip()) > 50
        ]

        if not valid_evidences:
            result["answer"] = "I don't know."
            return result

        # ✅ Chỉ khi evidence đủ mạnh mới generate
        rag_prompt = self.build_rag_prompt(
            question=question,
            evidences=valid_evidences
        )

        final_answer = generate_answer(rag_prompt)
        result["answer"] = final_answer

        return result

# Khởi tạo instance để các module khác (như API route) có thể import và sử dụng ngay
agent_service = AgentService()