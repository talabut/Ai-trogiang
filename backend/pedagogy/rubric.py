import json
from typing import List, Dict, Any

from backend.pedagogy.bloom import BloomLevel
from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import get_llm


CONTEXT_TOP_K = 5


def retrieve_context(topic: str) -> str:
    results = hybrid_search(topic)
    contexts = []

    for doc, _ in results[:CONTEXT_TOP_K]:
        contexts.append(doc.page_content)

    return "\n\n".join(contexts)


RUBRIC_PROMPT_TEMPLATE = """
Bạn là GIẢNG VIÊN.

NHIỆM VỤ:
Xây dựng RUBRIC CHẤM ĐIỂM cho bài học với mức độ Bloom: {bloom_level}

MÔ TẢ MỨC ĐỘ:
{bloom_description}

YÊU CẦU:
- Chỉ sử dụng thông tin trong TÀI LIỆU
- Rubric phải đánh giá đúng mức Bloom
- Có nhiều tiêu chí chấm điểm
- Có mô tả rõ cho từng mức điểm

TÀI LIỆU:
{context}

ĐỊNH DẠNG TRẢ VỀ (JSON):
[
  {{
    "criterion": "...",
    "levels": {{
      "excellent": "...",
      "good": "...",
      "average": "...",
      "poor": "..."
    }}
  }}
]
"""


def generate_rubric(
    topic: str,
    bloom: BloomLevel
) -> List[Dict[str, Any]]:
    """
    Generate grading rubric based on Bloom level
    """

    context = retrieve_context(topic)

    if not context.strip():
        raise ValueError("No relevant learning material found.")

    prompt = RUBRIC_PROMPT_TEMPLATE.format(
        bloom_level=bloom.value,
        bloom_description=bloom.description,
        context=context
    )

    llm = get_llm()
    raw = llm.invoke(prompt)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("LLM output is not valid JSON.")
