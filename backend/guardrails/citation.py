def format_citations(source_documents):
    citations = []
    for doc in source_documents:
        meta = doc.metadata
        citations.append({
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", None)
        })
    return citations
