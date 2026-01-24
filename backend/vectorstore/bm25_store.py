import pickle
from pathlib import Path
from typing import List, Tuple

from rank_bm25 import BM25Okapi
from langchain.schema import Document


BM25_PATH = Path("data/bm25.pkl")


class BM25Store:
    def __init__(self):
        self.documents: List[Document] = []
        self.corpus = []
        self.bm25 = None

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

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        return [
            (self.documents[idx], score)
            for idx, score in ranked
            if score > 0
        ]

    def save(self):
        BM25_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(BM25_PATH, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        if not BM25_PATH.exists():
            return BM25Store()

        with open(BM25_PATH, "rb") as f:
            return pickle.load(f)
