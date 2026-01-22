from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA

from backend.agent.prompt import SYSTEM_PROMPT
from backend.rag.retriever import get_retriever


def get_llm():
    pipe = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_new_tokens=256
    )
    return HuggingFacePipeline(pipeline=pipe)


def get_tutor_agent():
    llm = get_llm()
    retriever = get_retriever()

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )

    return qa
