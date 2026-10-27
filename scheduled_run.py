"""Script à configurer comme PythonAnywhere Scheduled Task, par exemple toutes les heures."""
from storage import save_run
from tester.runner import run_tests

if __name__ == "__main__":
    result = run_tests()
    run_id = save_run(result)
    print(
        f"Run #{run_id}: {result['summary']['passed']}/{result['summary']['total']} réussis, "
        f"latence moyenne {result['summary']['latency_ms_avg']} ms, "
        f"p95 {result['summary']['latency_ms_p95']} ms"
    )
