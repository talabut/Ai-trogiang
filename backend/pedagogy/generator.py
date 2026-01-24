import json
from typing import Dict, Any, List

from backend.pedagogy.bloom import BloomLevel
from backend.pedagogy.prompts import (
    build_question_prompt,
    build_assignment_prompt
)
from backend.rag.hybrid_retriever import hybrid_search
from backend.llm.llm import get_llm


CONTEXT_TOP_K = 5


def retrieve_context(query: str) -> str:
    """
    Retrieve learning context using Hybrid Search
    """
    results = hybrid_search(query)
    contexts = []

    for doc, score in results[:CONTEXT_TOP_K]:
        contexts.append(doc.page_content)

    return "\n\n".join(contexts)


def _invoke_llm(prompt: str) -> List[Dict[str, Any]]:
    """
    Invoke LLM and parse JSON output safely
    """
    llm = get_llm()
    raw = llm.invoke(prompt)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(
            "LLM output is not valid JSON. "
            "Please refine prompt or model configuration."
        )


def generate_questions(
    topic: str,
    bloom: BloomLevel,
    num_items: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate pedagogical questions based on Bloom level
    """

    context = retrieve_context(topic)

    if not context.strip():
        raise ValueError("No relevant learning material found.")

    prompt = build_question_prompt(
        context=context,
        bloom=bloom,
        num_items=num_items
    )

    return _invoke_llm(prompt)


def generate_assignments(
    topic: str,
    bloom: BloomLevel,
    num_items: int = 2
) -> List[Dict[str, Any]]:
    """
    Generate pedagogical assignments based on Bloom level
    """

    context = retrieve_context(topic)

    if not context.strip():
        raise ValueError("No relevant learning material found.")

    prompt = build_assignment_prompt(
        context=context,
        bloom=bloom,
        num_items=num_items
    )

    return _invoke_llm(prompt)
