# Atelier — Testing as Code & API Monitoring

## Objectif
Application Flask qui exécute des tests de contrat sur l'API publique Frankfurter, mesure quelques indicateurs de QoS et conserve l'historique des exécutions en SQLite.

API utilisée : https://api.frankfurter.app  
Documentation : https://www.frankfurter.app/docs/

## Fonctionnalités
- Six tests de contrat : HTTP/JSON, schéma de /latest, taux EUR→USD, /currencies, types des devises et paramètre de devise invalide.
- Client HTTP avec timeout de 4 s et un seul retry au maximum pour timeout réseau, HTTP 429 et erreurs serveur 5xx.
- Mesures calculées : latence moyenne, p95, taux d'échec des tests et disponibilité estimée de la suite.
- Application Flask avec page de consignes, dashboard, lancement manuel, détail de run, endpoint de santé et export JSON.
- Persistance de l'historique via SQLite.
- Workflow GitHub Actions pour tests unitaires et vérification de syntaxe à chaque push/PR sur main.
- Script compatible avec une Scheduled Task PythonAnywhere.

## Structure du projet
```text
.
├── flask_app.py
├── storage.py
├── scheduled_run.py
├── run_tests.py
├── requirements.txt
├── API_CHOICE.md
├── tester/
│   ├── __init__.py
│   ├── client.py
│   ├── tests.py
│   └── runner.py
├── tests/
│   └── test_runner.py
├── templates/
│   ├── consignes.html
│   ├── dashboard.html
│   └── run_detail.html
└── .github/workflows/
    ├── deploy-pythonanywhere.yml
    └── test-api.yml
```

## Exécution locale
Python 3.10+ recommandé.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run_tests.py
python flask_app.py
```

Puis ouvrir http://127.0.0.1:5000/ pour les consignes et http://127.0.0.1:5000/dashboard pour le dashboard.

## Routes
- `GET /` : consignes de l'atelier.
- `GET /dashboard` : dernier run et historique.
- `POST /run` : lance les six tests et enregistre le résultat.
- `GET /runs/<id>` : détail d'une exécution.
- `GET /health` : statut de l'application en JSON.
- `GET /export.json` : téléchargement de l'historique au format JSON.

## Déploiement PythonAnywhere
Le workflow `.github/workflows/deploy-pythonanywhere.yml` utilise les secrets de dépôt :
- `PA_USERNAME` : nom d'utilisateur PythonAnywhere.
- `PA_TOKEN` : API token PythonAnywhere.
- `PA_TARGET_DIR` : répertoire de code de l'application.
- `PA_WEBAPP_DOMAIN` : domaine de l'application, sans protocole.

Après le déploiement, vérifie la configuration WSGI et installe les dépendances dans l'environnement virtuel lié à l'application. Si l'application hébergée ne recharge pas automatiquement les dépendances, exécute `pip install -r /home/<username>/mysite/requirements.txt` dans la console PythonAnywhere adaptée, puis recharge la Web app.

**Attention au dossier de destination :** l'action téléverse/remplace les fichiers correspondants, mais ne supprime pas les fichiers distants qui n'existent plus dans GitHub. L'action recharge l'application configurée par `PA_WEBAPP_DOMAIN`.

## Tâche planifiée
Dans PythonAnywhere, crée une tâche planifiée qui exécute `scheduled_run.py` avec l'interpréteur Python de ton environnement virtuel, par exemple toutes les heures. Le script exécute la suite et écrit l'historique dans SQLite. Vérifie que le répertoire de travail et `ATELIER_DB_PATH` restent stables entre l'application Web et la tâche planifiée.

## Notes sur les métriques
- Le taux d'erreur correspond à la part de tests en échec dans la suite, ce n'est pas un taux d'erreur global mesuré sur le service distant.
- La disponibilité est une estimation basée sur la proportion de tests réussis lors d'un run.
- Le p95 est calculé sur les latences mesurées par les tests de ce run.
- Les tests sont en lecture seule. La suite utilise au plus six tests logiques, avec un maximum d'un retry par appel.
- Les valeurs obtenues dépendent de la disponibilité et de la latence de l'API publique au moment du test.

## Troubleshooting
Consulte les logs d'erreur et de serveur depuis l'onglet Web de PythonAnywhere. Les erreurs fréquentes incluent les dépendances non installées, un mauvais chemin WSGI ou un répertoire SQLite non accessible en écriture.
