from backend.rag.retriever import retrieve_docs
from backend.agent.tutor_agent import llm

def generate_task(task_request):
    docs = retrieve_docs(task_request.subject)
    context = "\n".join([d.page_content for d in docs])

    prompt = build_prompt(task_request, context)
    result = llm.invoke(prompt)

    return {
        "content": result,
        "sources": [d.metadata for d in docs]
    }
