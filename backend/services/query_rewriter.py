from backend.services.llm import generate_answer


class QueryRewriter:

    SYSTEM_PROMPT = (
        "You are an academic query rewriter.\n"
        "Rewrite the user's question into a clear, explicit, self-contained academic question.\n"
        "Preserve the original meaning.\n"
        "Do NOT answer the question.\n"
        "Only output the rewritten question.\n"
    )

    def rewrite(self, question: str) -> str:

        prompt = (
            f"{self.SYSTEM_PROMPT}\n"
            f"Original Question:\n{question}\n\n"
            "Rewritten Question:"
        )

        rewritten = generate_answer(prompt)

        if not rewritten or len(rewritten.strip()) < 5:
            return question

        return rewritten.strip()