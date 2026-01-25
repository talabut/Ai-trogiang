from backend.eval.datasets import EVAL_DATASET
from backend.eval.evaluator import evaluate_sample
from backend.logging.audit import audit_log

def run_evaluation():
    results = []

    for sample in EVAL_DATASET:
        result = evaluate_sample({
            "id": sample.id,
            "question": sample.question
        })

        results.append(result)

        audit_log(
            user="system_eval",
            action="evaluation_run",
            payload=result
        )

    return results
