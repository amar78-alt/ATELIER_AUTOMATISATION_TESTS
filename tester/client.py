"""Client HTTP simple et robuste pour Frankfurter."""

import time
import requests

BASE_URL = "https://api.frankfurter.app"
TIMEOUT_SECONDS = 4


def get_json(path, params=None, retries=1):
    """Effectue une requête GET, mesure la latence et limite les retries."""
    url = BASE_URL + path
    last_error = None

    for attempt in range(retries + 1):
        started = time.perf_counter()
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
            latency_ms = round((time.perf_counter() - started) * 1000, 2)

            # En cas de rate limit ou d'erreur serveur, réessayer au plus une fois.
            if response.status_code == 429 or response.status_code >= 500:
                last_error = RuntimeError("HTTP " + str(response.status_code))
                if attempt < retries:
                    time.sleep(1)
                    continue

            response.raise_for_status()
            try:
                payload = response.json()
            except ValueError as exc:
                raise ValueError("La réponse n'est pas un JSON valide.") from exc

            return {
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "json": payload,
                "latency_ms": latency_ms,
            }

        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1)
                continue
            raise RuntimeError("Échec de la requête vers " + url + ": " + str(exc)) from exc

    raise RuntimeError("Échec de la requête : " + str(last_error))
