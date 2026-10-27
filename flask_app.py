"""Application Flask de surveillance de l'API Frankfurter."""

from datetime import datetime, timezone
import json

from flask import Flask, jsonify, redirect, render_template, request, url_for, make_response

from storage import get_run, init_db, list_runs
from tester.runner import run_and_store

app = Flask(__name__)


@app.get("/")
def consignes():
    """Conserver les consignes d'origine accessibles à la racine."""
    return render_template("consignes.html")


@app.get("/dashboard")
def dashboard():
    init_db()
    history_rows = list_runs(limit=50)
    history = []
    latest = None

    for row in history_rows:
        try:
            tests = json.loads(row["results_json"])
        except (TypeError, ValueError):
            tests = []
        item = {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "api": row["api"],
            "passed": row["passed"],
            "failed": row["failed"],
            "error_rate": row["error_rate"],
            "availability": round((row["passed"] / (row["passed"] + row["failed"])) * 100, 2)
                if (row["passed"] + row["failed"]) else 0,
            "latency_avg": row["latency_avg"],
            "latency_p95": row["latency_p95"],
            "tests": tests,
        }
        history.append(item)

    if history:
        latest = history[0]

    return render_template("dashboard.html", latest=latest, history=history)


@app.post("/run")
def run_tests():
    """Déclenche un run non destructif et redirige vers le dashboard."""
    run_and_store()
    return redirect(url_for("dashboard"))


@app.get("/run/<int:run_id>")
def run_detail(run_id):
    row = get_run(run_id)
    if row is None:
        return render_template("404.html"), 404
    try:
        tests = json.loads(row["results_json"])
    except (TypeError, ValueError):
        tests = []
    total = row["passed"] + row["failed"]
    detail = {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "api": row["api"],
        "summary": {
            "passed": row["passed"],
            "failed": row["failed"],
            "error_rate": row["error_rate"],
            "latency_avg": row["latency_avg"],
            "latency_p95": row["latency_p95"],
            "availability": round((row["passed"] / total) * 100, 2) if total else 0,
        },
        "tests": tests,
    }
    return render_template("run_detail.html", run=detail)


@app.get("/health")
def health():
    """État de santé applicatif local ; ne déclenche pas un run externe."""
    init_db()
    return jsonify({
        "status": "ok",
        "service": "API Watch",
        "api": "Frankfurter",
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    })


@app.get("/export.json")
def export_json():
    """Exporte le dernier run en JSON."""
    rows = list_runs(limit=1)
    if not rows:
        return jsonify({"message": "Aucun run n'a encore été enregistré."}), 404
    row = rows[0]
    try:
        tests = json.loads(row["results_json"])
    except (TypeError, ValueError):
        tests = []
    payload = {
        "api": row["api"],
        "timestamp": row["timestamp"],
        "summary": {
            "passed": row["passed"],
            "failed": row["failed"],
            "error_rate": row["error_rate"],
            "latency_ms_avg": row["latency_avg"],
            "latency_ms_p95": row["latency_p95"],
        },
        "tests": tests,
    }
    response = make_response(json.dumps(payload, ensure_ascii=False, indent=2))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Content-Disposition"] = 'attachment; filename="latest-run.json"'
    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
