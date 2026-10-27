"""Tests de contrat de l'API Frankfurter. Chaque fonction retourne un résultat structuré."""
from __future__ import annotations

from tester.client import get


def _result(name: str, response, condition: bool, details: str) -> dict:
    return {
        "name": name,
        "status": "PASS" if condition else "FAIL",
        "status_code": response.status_code,
        "latency_ms": round(response.elapsed_ms, 2),
        "details": details,
        "url": response.url,
    }


def test_latest_json() -> dict:
    response = get("/latest", {"from": "EUR"})
    ok = response.status_code == 200 and "json" in response.content_type.lower()
    return _result("1. /latest répond en JSON", response, ok, "HTTP 200 et Content-Type JSON attendus")


def test_latest_schema() -> dict:
    response = get("/latest", {"from": "EUR"})
    data = response.json_data
    ok = (
        response.status_code == 200
        and isinstance(data, dict)
        and isinstance(data.get("amount"), (int, float))
        and isinstance(data.get("base"), str)
        and isinstance(data.get("date"), str)
        and isinstance(data.get("rates"), dict)
    )
    return _result("2. Schéma de /latest", response, ok, "amount numérique, base/date texte, rates objet")


def test_usd_rate() -> dict:
    response = get("/latest", {"from": "EUR", "to": "USD"})
    rates = response.json_data.get("rates", {}) if isinstance(response.json_data, dict) else {}
    value = rates.get("USD")
    ok = response.status_code == 200 and isinstance(value, (int, float)) and value > 0
    return _result("3. Taux EUR vers USD", response, ok, "rates.USD doit être numérique et positif")


def test_currencies_json() -> dict:
    response = get("/currencies")
    data = response.json_data
    ok = response.status_code == 200 and "json" in response.content_type.lower() and isinstance(data, dict)
    return _result("4. /currencies répond en JSON", response, ok, "HTTP 200 et objet JSON attendus")


def test_currency_schema() -> dict:
    response = get("/currencies")
    data = response.json_data
    some_entry_ok = isinstance(data, dict) and bool(data) and all(
        isinstance(key, str) and isinstance(value, str) for key, value in list(data.items())[:10]
    )
    ok = response.status_code == 200 and some_entry_ok
    return _result("5. Schéma de /currencies", response, ok, "Codes et noms de devises doivent être des textes")


def test_invalid_base_currency() -> dict:
    response = get("/latest", {"from": "NOTACURRENCY"})
    # Le contrat attendu est une erreur : on accepte un statut HTTP 4xx
    # ou une réponse non exploitable, et on échoue si l'API annonce un succès valide.
    data = response.json_data
    invalid = (
        response.status_code is not None
        and (response.status_code >= 400 or not isinstance(data, dict) or "rates" not in data)
    )
    return _result(
        "6. Devise de base invalide",
        response,
        invalid,
        "Une devise inconnue ne doit pas produire un objet de taux normal valide",
    )


TESTS = [
    test_latest_json,
    test_latest_schema,
    test_usd_rate,
    test_currencies_json,
    test_currency_schema,
    test_invalid_base_currency,
]
