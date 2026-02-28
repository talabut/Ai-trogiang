from backend.infra.rag.retrieval_impl import LlamaRetriever

COURSE_ID = "your_course_id_here"   # đổi đúng course_id bạn đã upload

def test_retrieval():
    retriever = LlamaRetriever(course_id=COURSE_ID)

    query = "định nghĩa marketing là gì"  # đổi thành câu hỏi thật

    nodes = retriever.retrieve(query)

    print("\n=== RETRIEVAL RESULT ===")
    for i, node in enumerate(nodes):
        print(f"\nRank {i+1}")
        print("Score:", node.score)
        print("Content preview:", node.node.get_content()[:500])


if __name__ == "__main__":
    test_retrieval()