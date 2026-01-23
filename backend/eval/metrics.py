def groundedness_score(source_documents, expected_sources):
    if not source_documents:
        return 0.0

    matched = 0
    for doc in source_documents:
        src = doc.metadata.get("source", "")
        if any(exp in src for exp in expected_sources):
            matched += 1

    return matched / len(expected_sources)


def citation_coverage(source_documents):
    if not source_documents:
        return 0.0
    cited_pages = [
        doc.metadata.get("page") for doc in source_documents
        if doc.metadata.get("page") is not None
    ]
    return len(cited_pages) / len(source_documents)


def hallucination_flag(source_documents):
    return len(source_documents) == 0
