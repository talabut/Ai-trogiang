import json
from typing import Dict, Any, List

from backend.agent.qa import answer_question
from backend.eval.groundedness import check_groundedness
from backend.eval.faithfulness import check_faithfulness


DATASET_PATH = "backend/eval/dataset.json"


def load_dataset() -> Dict[str, Any]:
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


def evaluate_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    question = sample["question"]

    result = answer_question(question)

    answer = result.get("answer", "")
    sources = result.get("sources", [])

    contexts = [
        src.get("preview", "")
        for src in sources
        if src.get("preview")
    ]

    groundedness = check_groundedness(answer, sources)
    faithfulness = check_faithfulness(answer, contexts)

    return {
        "id": sample["id"],
        "question": question,
        "answer": answer,
        "groundedness": groundedness,
        "faithfulness": faithfulness,
        "sources_count": len(sources)
    }


def run_evaluation() -> Dict[str, Any]:
    dataset = load_dataset()
    samples = dataset.get("samples", [])

    results: List[Dict[str, Any]] = []

    grounded_ok = 0
    faithful_ok = 0

    for sample in samples:
        print(f"Evaluating: {sample['id']} – {sample['question']}")
        result = evaluate_sample(sample)
        results.append(result)

        if result["groundedness"]["grounded"]:
            grounded_ok += 1
        if result["faithfulness"]["faithful"]:
            faithful_ok += 1

    total = len(samples)

    summary = {
        "total": total,
        "groundedness_rate": round(grounded_ok / total, 2),
        "faithfulness_rate": round(faithful_ok / total, 2)
    }

    report = {
        "summary": summary,
        "results": results
    }

    return report


if __name__ == "__main__":
    report = run_evaluation()
    print("\n=== EVALUATION SUMMARY ===")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
