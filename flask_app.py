"""Application Flask : consignes, exécution des tests et tableau de bord."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from threading import Lock

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

from storage import get_run, init_db, list_runs, save_run
from tester.runner import run_tests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "atelier-testing-as-code-development-key")
RUN_LOCK = Lock()
_last_run_monotonic = 0.0
MIN_RUN_INTERVAL_SECONDS = 60  # anti-spam minimal côté application
MAX_RUNS_PER_HOUR = 12
_run_times: list[float] = []


@app.before_request
def prepare_database():
    init_db()


@app.get("/")
def consignes():
    return render_template("consignes.html")


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "atelier-testing-as-code",
        "api": "Frankfurter",
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })


@app.get("/dashboard")
def dashboard():
    history = list_runs(limit=20)
    latest = get_run(history[0]["id"]) if history else None
    return render_template("dashboard.html", latest=latest, runs=history)


@app.post("/run")
def run_tests_route():
    global _last_run_monotonic, _run_times
    now = time.monotonic()
    with RUN_LOCK:
        _run_times = [stamp for stamp in _run_times if now - stamp < 3600]
        if now - _last_run_monotonic < MIN_RUN_INTERVAL_SECONDS:
            flash("Attends au moins 60 secondes entre deux exécutions.")
            return redirect(url_for("dashboard"))
        if len(_run_times) >= MAX_RUNS_PER_HOUR:
            flash("Limite de sécurité atteinte : 12 exécutions maximum par heure.")
            return redirect(url_for("dashboard"))
        _last_run_monotonic = now
        _run_times.append(now)

    result = run_tests()
    run_id = save_run(result)
    flash(f"Exécution #{run_id} terminée : {result['summary']['passed']} réussi(s), {result['summary']['failed']} échec(s).")
    return redirect(url_for("run_detail", run_id=run_id))


@app.get("/runs/<int:run_id>")
def run_detail(run_id: int):
    result = get_run(run_id)
    if result is None:
        abort(404)
    return render_template("run_detail.html", run=result)


@app.get("/export.json")
def export_runs():
    history = list_runs(limit=100)
    details = [get_run(item["id"]) for item in history]
    response = jsonify({"exported_at": datetime.now(timezone.utc).isoformat(), "runs": details})
    response.headers["Content-Disposition"] = 'attachment; filename="atelier-runs.json"'
    return response


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "not_found"}), 404
    return "Page introuvable (404). <a href='/dashboard'>Retour au dashboard</a>", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
