import json
import sys
import os

# Cho phép import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.services.agent import AgentService  # chỉnh đúng path nếu khác


COURSE_ID = "ml_course"
SESSION_ID = "eval_session"


def compute_retrieval_recall(evidences, expected_keywords):
    if not evidences:
        return 0.0

    text_blob = " ".join(ev.get("text", "") for ev in evidences).lower()

    hits = sum(
        1 for kw in expected_keywords
        if kw.lower() in text_blob
    )

    return hits / max(len(expected_keywords), 1)


def run():
    agent = AgentService()

    with open("tests/evaluation/test_set.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total = len(test_cases)
    recall_scores = []
    grounding_pass = 0
    hallucinations = 0

    for case in test_cases:
        response = agent.chat(
            question=case["question"],
            session_id=SESSION_ID,
            course_id=COURSE_ID
        )

        evidences = response.get("evidences", [])
        recall = compute_retrieval_recall(
            evidences,
            case["expected_keywords"]
        )

        recall_scores.append(recall)

        if response.get("confidence", 0) > 0.5:
            grounding_pass += 1

        if recall < 0.5:
            hallucinations += 1

        print(f"\n===== Q{case['id']} =====")
        print("Question:", case["question"])
        print("Expected Keywords:", case["expected_keywords"])
        print("Recall:", recall)

        print("\n--- Evidences ---")
        for i, ev in enumerate(evidences):
            print(f"\nEvidence {i+1}")
            print("Text:", ev.get("text", "")[:300])
            print("Metadata:", ev.get("metadata"))

    print("\n===== SUMMARY =====")
    print("Total:", total)
    print("Avg Recall:", sum(recall_scores) / total)
    print("Grounding Rate:", grounding_pass / total)
    print("Hallucination Rate:", hallucinations / total)


if __name__ == "__main__":
    run()