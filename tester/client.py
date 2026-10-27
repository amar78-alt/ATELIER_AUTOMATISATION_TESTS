"""Client HTTP Frankfurter avec timeout et un seul retry en cas d'erreur temporaire."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
    """Effectue un GET et renvoie le statut, le JSON éventuel et la latence."""
    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"

    last_error: str | None = None
    last_elapsed_ms = 0.0

    for attempt in range(MAX_ATTEMPTS):
        started = time.perf_counter()
        try:
            req = Request(url, headers={"Accept": "application/json", "User-Agent": "atelier-api-monitor/1.0"})
            with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                body = response.read()
                last_elapsed_ms = (time.perf_counter() - started) * 1000
                content_type = response.headers.get("Content-Type", "")
                try:
                    data = json.loads(body.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    data = None
                return ApiResponse(
                    url=response.geturl(),
                    status_code=response.status,
                    content_type=content_type,
                    elapsed_ms=last_elapsed_ms,
                    json_data=data,
                )
        except HTTPError as exc:
            last_elapsed_ms = (time.perf_counter() - started) * 1000
            last_error = f"HTTP {exc.code}"
            content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
            try:
                data = json.loads(exc.read().decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                data = None

            if (exc.code == 429 or exc.code >= 500) and attempt + 1 < MAX_ATTEMPTS:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    delay = min(float(retry_after), 2.0) if retry_after else 0.5
                except ValueError:
                    delay = 0.5
                time.sleep(max(delay, 0.0))
                continue

            return ApiResponse(url, exc.code, content_type, last_elapsed_ms, data, last_error)
        except (URLError, TimeoutError, OSError) as exc:
            last_elapsed_ms = (time.perf_counter() - started) * 1000
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt + 1 < MAX_ATTEMPTS:
                time.sleep(0.3)

    return ApiResponse(url, None, "", last_elapsed_ms, None, last_error or "Erreur réseau inconnue")
