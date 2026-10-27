"""Exécution des tests et calcul des indicateurs QoS."""

from datetime import datetime, timezone
import math
from statistics import mean

from .tests import run_tests
from storage import save_run


def percentile95(values):
    """Percentile 95 avec interpolation linéaire simple."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 2)
    position = 0.95 * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 2)
    fraction = position - lower
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * fraction, 2)


def run_and_store():
    results = run_tests()
    passed = sum(1 for result in results if result["status"] == "PASS")
    failed = len(results) - passed
    latencies = [
        result["latency_ms"] for result in results
        if isinstance(result.get("latency_ms"), (int, float))
    ]
    total = len(results)
    summary = {
        "passed": passed,
        "failed": failed,
        "total": total,
        "error_rate": round(failed / total, 4) if total else 0,
        "availability": round(passed / total * 100, 2) if total else 0,
        "latency_avg": round(mean(latencies), 2) if latencies else None,
        "latency_p95": percentile95(latencies),
    }
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    run_id = save_run(timestamp, summary, results)
    return {
        "id": run_id,
        "timestamp": timestamp,
        "api": "Frankfurter",
        "summary": summary,
        "tests": results,
    }
