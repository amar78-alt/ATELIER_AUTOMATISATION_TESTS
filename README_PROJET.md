# API Watch — Atelier automatisation des tests

Ce dépôt met en place une solution de tests automatisés pour l'API publique Frankfurter.

## API choisie
- Base URL : https://api.frankfurter.app
- Documentation : https://frankfurter.dev/
- Authentification : aucune pour les endpoints utilisés.
- Endpoints : `GET /latest?from=EUR` et `GET /latest?from=USD&to=EUR`.

Le contrat et les hypothèses sont documentés dans [API_CHOICE.md](API_CHOICE.md).

## Exécution locale
1. Utiliser Python 3.10 ou plus récent.
2. Installer les dépendances : `python -m pip install -r requirements.txt`.
3. Lancer un run : `python run_tests.py`.
4. Lancer le site : `python flask_app.py`, puis visiter `http://127.0.0.1:5000/dashboard`.

Chaque run exécute 7 contrôles et enregistre les résultats dans SQLite (`runs.db`). La base est créée à la première exécution et n'est pas nécessairement versionnée dans Git.

## Routes Flask
- `/` : consignes d'origine de l'atelier.
- `/dashboard` : dernières mesures et historique.
- `POST /run` : exécute les tests et sauvegarde les résultats.
- `/run/<id>` : détail d'une exécution.
- `/health` : état de santé de l'application.
- `/export.json` : télécharge le dernier run au format JSON.

## Mesures QoS
- Latence moyenne des requêtes qui ont fourni une mesure.
- Percentile de latence p95 des requêtes mesurées.
- Taux d'échec des tests et disponibilité calculée sur le nombre de tests réussis.
- Historique des runs, horodatages, détail des tests et messages d'échec.

## Bonnes pratiques
Les appels sont en lecture seule, avec un timeout strict de 4 secondes, une seule nouvelle tentative maximale et une pause courte en cas d'erreur temporaire. Ne pas exécuter le run en boucle : respecter la limite indicative de l'atelier (environ un run toutes les 5 minutes et au maximum 20 requêtes par run).

## Déploiement
Le dépôt contient un workflow de déploiement PythonAnywhere fourni par le squelette du professeur. Il nécessite les secrets `PA_USERNAME`, `PA_TOKEN`, `PA_TARGET_DIR`, `PA_WEBAPP_DOMAIN` ainsi que, si nécessaire, `PA_HOST`. Avant de l'activer, vérifier impérativement que le chemin cible ne pointe pas vers le dossier de ton premier atelier : cela pourrait remplacer ses fichiers.
