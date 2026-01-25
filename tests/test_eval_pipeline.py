from backend.eval.runner import run_evaluation

def test_eval_runs():
    results = run_evaluation()
    assert isinstance(results, list)
    assert "grounded" in results[0]
