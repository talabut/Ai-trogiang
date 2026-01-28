import g4f
from langchain_community.llms import G4FLLM

# Sử dụng G4F (GPT4Free) - Không cần API Key, chạy qua các cổng miễn phí của bên thứ 3
llm_instance = G4FLLM(
    model=g4f.models.gpt_35_turbo, # Bạn có thể thử g4f.models.llama_3
)

def get_llm():
    return llm_instance