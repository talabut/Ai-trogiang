from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

from backend.agent.prompt import SYSTEM_PROMPT
from backend.rag.retriever import get_retriever
from backend.guardrails.grounding import check_grounding


def get_llm():
    pipe = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_new_tokens=512
    )
    return HuggingFacePipeline(pipeline=pipe)


def get_tutor_agent():
    llm = get_llm()
    retriever = get_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )

    def guarded_run(query: str):
        result = qa_chain(query)
        check_grounding(result["source_documents"])
        return result

    return guarded_run
