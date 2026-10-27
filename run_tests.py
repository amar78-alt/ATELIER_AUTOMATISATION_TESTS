"""Lanceur en ligne de commande pour exécuter et afficher le rapport JSON."""
import json
from tester.runner import run_tests

if __name__ == "__main__":
    result = run_tests()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["summary"]["failed"] == 0 else 1)
