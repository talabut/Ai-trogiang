from backend.tools.search import search_docs

def summarize_topic(topic: str):
    content = search_docs(topic)
    if not content:
        return "Không tìm thấy tài liệu để tóm tắt."

    return f"Tóm tắt nội dung:\n{content[:1500]}"
