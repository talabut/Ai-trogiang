from backend.rag.retrieval import retrieve_documents

if not callable(retrieve_documents):
    raise RuntimeError("retrieve_documents missing")

def sanitize_prompt(text: str) -> str:
    banned = ["system:", "ignore previous", "override"]
    for b in banned:
        text = text.replace(b, "")
    return text[:2000]

class AgentService:
    async def ask(self, question: str, session_id: str, threshold=None):
        q = sanitize_prompt(question)
        docs = retrieve_documents(query=q, top_k=5, threshold=threshold)
        if not docs:
            return "Không tìm thấy thông tin phù hợp."
        return "\n".join(d["content"] for d in docs)
