"""Lance les tests API depuis la ligne de commande."""

import json
from tester.runner import run_and_store


if __name__ == "__main__":
    result = run_and_store()
    print(json.dumps(result, ensure_ascii=False, indent=2))
