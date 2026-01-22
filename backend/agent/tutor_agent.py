from transformers import pipeline

from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from backend.agent.prompt import SYSTEM_PROMPT
from backend.rag.retriever import get_retriever


def get_llm():
    pipe = pipeline(
        "text-generation",
        model="google/flan-t5-base",
        max_new_tokens=512
    )
    return HuggingFacePipeline(pipeline=pipe)


def get_tutor_agent():
    llm = get_llm()
    retriever = get_retriever()

    prompt = PromptTemplate.from_template(
        SYSTEM_PROMPT
        + """
        ----------------
        TÀI LIỆU:
        {context}

        CÂU HỎI:
        {question}

        TRẢ LỜI (chỉ dựa trên tài liệu):
        """
    )

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )

    return chain
