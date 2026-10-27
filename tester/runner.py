"""Exécution du plan de tests et calcul des métriques QoS."""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone

from tester.tests import TESTS


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(percentile * len(ordered)) - 1))
    return round(ordered[index], 2)


def run_tests() -> dict:
    started_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    started = time.perf_counter()
    results = []

    for test in TESTS:
        try:
            results.append(test())
        except Exception as exc:  # un test en erreur ne doit pas interrompre toute la suite
            results.append({
                "name": getattr(test, "__name__", "test inconnu"),
                "status": "FAIL",
                "status_code": None,
                "latency_ms": 0,
                "details": f"Erreur inattendue : {type(exc).__name__}: {exc}",
                "url": "",
            })

    total = len(results)
    passed = sum(item["status"] == "PASS" for item in results)
    failed = total - passed
    latencies = [float(item.get("latency_ms", 0)) for item in results]
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "api": "Frankfurter",
        "timestamp": started_at,
        "duration_ms": duration_ms,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error_rate": round(failed / total, 4) if total else 0.0,
            "availability": round(passed / total * 100, 2) if total else 0.0,
            "latency_ms_avg": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
            "latency_ms_p95": _percentile(latencies, 0.95),
        },
        "tests": results,
    }
