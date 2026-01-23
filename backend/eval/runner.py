from backend.eval.datasets import EVAL_DATASET
from backend.eval.evaluator import evaluate_sample
from backend.logging.audit import audit_log


def run_evaluation():
    results = []

    for sample in EVAL_DATASET:
        r = evaluate_sample(sample)
        results.append(r)

        audit_log(
            user_id="system_eval",
            action="eval",
            payload=r
        )

    return results


if __name__ == "__main__":
    report = run_evaluation()
    for r in report:
        print(r)
