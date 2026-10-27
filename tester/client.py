"""Client HTTP de l'API Frankfurter avec timeout et une seule tentative de reprise."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

BASE_URL = "https://api.frankfurter.app"
TIMEOUT_SECONDS = 4
MAX_ATTEMPTS = 2  # premier appel + un seul retry


@dataclass
class ApiResponse:
    url: str
    status_code: int | None
    content_type: str
    elapsed_ms: float
    json_data: Any = None
    error: str | None = None


def get(path: str, params: dict[str, str] | None = None) -> ApiResponse:
    """Effectue une requête GET et mesure le temps total d'une tentative réussie."""
    url = f"{BASE_URL}{path}"
    last_error = None

    for attempt in range(MAX_ATTEMPTS):
        started = time.perf_counter()
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
            elapsed_ms = (time.perf_counter() - started) * 1000
            content_type = response.headers.get("Content-Type", "")
            try:
                json_data = response.json()
            except ValueError:
                json_data = None

            # Retry uniquement sur 429 et erreurs serveur temporaires.
            if response.status_code == 429 or response.status_code >= 500:
                last_error = f"HTTP {response.status_code}"
                if attempt + 1 < MAX_ATTEMPTS:
                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = min(float(retry_after), 2.0) if retry_after else 0.5
                    except ValueError:
                        delay = 0.5
                    time.sleep(max(delay, 0))
                    continue

            return ApiResponse(
                url=response.url,
                status_code=response.status_code,
                content_type=content_type,
                elapsed_ms=elapsed_ms,
                json_data=json_data,
                error=last_error,
            )
        except requests.RequestException as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt + 1 < MAX_ATTEMPTS:
                time.sleep(0.3)

    return ApiResponse(
        url=url,
        status_code=None,
        content_type="",
        elapsed_ms=TIMEOUT_SECONDS * 1000,
        json_data=None,
        error=last_error or "Erreur réseau inconnue",
    )
