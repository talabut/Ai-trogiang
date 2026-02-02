from backend.infra.rag.retrieval_impl import FaissRetriever
from backend.core.interfaces import IRetriever

_retriever: IRetriever = FaissRetriever()

def retrieve_documents(
    query: str,
    top_k: int = 5,
    threshold: float | None = None
):
    return _retriever.retrieve(query, top_k=top_k, threshold=threshold)
