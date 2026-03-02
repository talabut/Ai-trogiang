from backend.services.llm import generate_answer


class QueryExpander:
    """
    Sinh câu truy vấn mở rộng phục vụ multi-hop retrieval.
    Không dùng cho answering.
    """

    def expand(self, question: str, first_evidences: list) -> str:
        if not first_evidences:
            return question

        context_preview = "\n".join(
            ev["text"][:300] for ev in first_evidences[:2]
        )

        prompt = (
            "You are helping expand a search query for academic retrieval.\n"
            "Given the QUESTION and partial CONTEXT,\n"
            "Generate ONE short expanded search query that helps retrieve\n"
            "related definitions, conditions, or relationships.\n"
            "Return only the expanded query.\n\n"
            f"QUESTION:\n{question}\n\n"
            f"PARTIAL CONTEXT:\n{context_preview}\n\n"
            "EXPANDED QUERY:"
        )

        expanded = generate_answer(prompt)

        if not expanded:
            return question

        return expanded.strip()