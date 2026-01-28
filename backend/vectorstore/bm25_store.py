import pickle
from pathlib import Path
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

class BM25Store:
    def __init__(self, course_id: str):
        self.course_id = course_id
        self.documents: List[Document] = []
        self.corpus = []
        self.bm25 = None
        self.storage_path = Path(f"data/bm25_{course_id}.pkl") # Tách biệt theo course [cite: 82]

    def add_documents(self, docs: List[Document]):
        for doc in docs:
            tokens = doc.page_content.lower().split()
            self.documents.append(doc)
            self.corpus.append(tokens)
        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        if not self.bm25:
            return []
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
        return [(self.documents[idx], score) for idx, score in ranked if score > 0]

    def save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, course_id: str):
        """
        FIX: Trả về một instance đã load dữ liệu thay vì instance trống 
        """
        instance = cls(course_id)
        if instance.storage_path.exists():
            with open(instance.storage_path, "rb") as f:
                loaded_data = pickle.load(f)
                instance.documents = loaded_data.documents
                instance.corpus = loaded_data.corpus
                instance.bm25 = loaded_data.bm25
        return instance