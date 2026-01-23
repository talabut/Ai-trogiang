from dataclasses import dataclass
from typing import List

@dataclass
class EvalSample:
    question: str
    expected_sources: List[str]  # filename hoặc keyword
    difficulty: str              # easy / medium / hard


EVAL_DATASET = [
    EvalSample(
        question="Định nghĩa trí tuệ nhân tạo là gì?",
        expected_sources=["ai_intro.pdf"],
        difficulty="easy"
    ),
    EvalSample(
        question="Sự khác nhau giữa supervised và unsupervised learning?",
        expected_sources=["machine_learning.pdf"],
        difficulty="medium"
    ),
]
