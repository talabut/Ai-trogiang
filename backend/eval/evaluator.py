from backend.agent.tutor_agent import get_tutor_agent
from backend.eval.metrics import (
    groundedness_score,
    citation_coverage,
    hallucination_flag
)

agent = get_tutor_agent()


def evaluate_sample(sample):
    result = agent(sample.question)

    groundedness = groundedness_score(
        result["source_documents"],
        sample.expected_sources
    )

    citation = citation_coverage(result["source_documents"])
    hallucinated = hallucination_flag(result["source_documents"])

    return {
        "question": sample.question,
        "groundedness": groundedness,
        "citation_coverage": citation,
        "hallucinated": hallucinated
    }
