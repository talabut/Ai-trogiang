from backend.pedagogy.bloom import BloomLevel


QUESTION_PROMPT_TEMPLATE = """
Bạn là AI Trợ Giảng.

NHIỆM VỤ:
Sinh {num_items} CÂU HỎI học tập theo mức độ Bloom: {bloom_level}

MÔ TẢ MỨC ĐỘ:
{bloom_description}

YÊU CẦU BẮT BUỘC:
- CHỈ sử dụng thông tin trong TÀI LIỆU bên dưới
- Không suy đoán, không thêm kiến thức bên ngoài
- Mỗi câu hỏi phải bám sát nội dung tài liệu
- Mức độ nhận thức phải đúng Bloom level
- Không trùng lặp câu hỏi

TÀI LIỆU:
{context}

ĐỊNH DẠNG TRẢ VỀ (JSON):
[
  {{
    "question": "...",
    "bloom_level": "{bloom_level}",
    "learning_objective": "...",
    "difficulty": "easy | medium | hard"
  }}
]
"""


ASSIGNMENT_PROMPT_TEMPLATE = """
Bạn là AI Trợ Giảng.

NHIỆM VỤ:
Sinh {num_items} BÀI TẬP học tập theo mức độ Bloom: {bloom_level}

MÔ TẢ MỨC ĐỘ:
{bloom_description}

YÊU CẦU BẮT BUỘC:
- CHỈ sử dụng thông tin trong TÀI LIỆU bên dưới
- Không suy đoán, không thêm kiến thức bên ngoài
- Bài tập phải yêu cầu người học vận dụng đúng mức Bloom
- Có mô tả rõ yêu cầu đầu ra

TÀI LIỆU:
{context}

ĐỊNH DẠNG TRẢ VỀ (JSON):
[
  {{
    "title": "...",
    "task": "...",
    "expected_output": "...",
    "bloom_level": "{bloom_level}",
    "difficulty": "easy | medium | hard"
  }}
]
"""


def build_question_prompt(
    context: str,
    bloom: BloomLevel,
    num_items: int = 3
) -> str:
    return QUESTION_PROMPT_TEMPLATE.format(
        num_items=num_items,
        bloom_level=bloom.value,
        bloom_description=bloom.description,
        context=context
    )


def build_assignment_prompt(
    context: str,
    bloom: BloomLevel,
    num_items: int = 2
) -> str:
    return ASSIGNMENT_PROMPT_TEMPLATE.format(
        num_items=num_items,
        bloom_level=bloom.value,
        bloom_description=bloom.description,
        context=context
    )
