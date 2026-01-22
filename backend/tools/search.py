from backend.rag.retriever import get_retriever

def search_docs(query: str):
    retriever = get_retriever()
    docs = retriever.get_relevant_documents(query)

    if not docs:
        return None

    return "\n".join([doc.page_content for doc in docs])
