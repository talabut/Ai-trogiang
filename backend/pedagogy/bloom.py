from enum import Enum
from typing import List


class BloomLevel(str, Enum):
    """
    Bloom's Taxonomy – Cognitive Domain
    """

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

    @property
    def description(self) -> str:
        return {
            self.REMEMBER: "Nhớ lại thông tin, định nghĩa, thuật ngữ",
            self.UNDERSTAND: "Giải thích, mô tả, diễn giải ý nghĩa",
            self.APPLY: "Áp dụng kiến thức vào bài toán cụ thể",
            self.ANALYZE: "Phân tích, so sánh, chỉ ra mối quan hệ",
            self.EVALUATE: "Đánh giá, nhận xét, phản biện",
            self.CREATE: "Tổng hợp, thiết kế, xây dựng mới"
        }[self]

    @property
    def action_verbs(self) -> List[str]:
        """
        Gợi ý động từ dùng trong câu hỏi / bài tập
        """
        return {
            self.REMEMBER: ["liệt kê", "nêu", "định nghĩa", "kể tên"],
            self.UNDERSTAND: ["giải thích", "trình bày", "mô tả", "tóm tắt"],
            self.APPLY: ["áp dụng", "tính toán", "giải", "thực hiện"],
            self.ANALYZE: ["phân tích", "so sánh", "phân loại", "làm rõ"],
            self.EVALUATE: ["đánh giá", "nhận xét", "phản biện", "so sánh ưu nhược điểm"],
            self.CREATE: ["thiết kế", "xây dựng", "đề xuất", "phát triển"]
        }[self]

    @classmethod
    def ordered_levels(cls) -> List["BloomLevel"]:
        """
        Trả về Bloom levels theo thứ tự tăng dần độ khó
        """
        return [
            cls.REMEMBER,
            cls.UNDERSTAND,
            cls.APPLY,
            cls.ANALYZE,
            cls.EVALUATE,
            cls.CREATE
        ]
