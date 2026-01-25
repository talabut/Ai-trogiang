from backend.eval.runner import run_evaluation

def test_eval_pipeline_runs():
    results = run_evaluation()
    assert isinstance(results, list)
    assert len(results) > 0
    assert "score" in results[0]
