from dataclasses import dataclass
from typing import List

@dataclass
class EvalSample:
    id: int
    question: str
    expected_answer: str | None = None

EVAL_DATASET: List[EvalSample] = [
    EvalSample(
        id=1,
        question="FAISS là gì trong hệ thống RAG?"
    ),
    EvalSample(
        id=2,
        question="BM25 dùng để làm gì?"
    ),
]
