# Choix d’API — Frankfurter

- Étudiant : Alle Amar
- API choisie : Frankfurter
- URL de base : https://api.frankfurter.app
- Documentation officielle : https://www.frankfurter.app/docs/
- Authentification : aucune clé requise pour les endpoints utilisés.

## Endpoints testés

- `GET /latest?from=EUR` : récupère les derniers taux disponibles depuis l’euro.
- `GET /latest?from=EUR&to=USD` : récupère le taux EUR vers USD.
- `GET /currencies` : récupère la liste des devises prises en charge.

## Contrat attendu

- Réponse HTTP 200 pour les requêtes valides.
- Le corps est du JSON.
- Pour `/latest`, la réponse contient `amount` (nombre), `base` (texte), `date` (texte au format date) et `rates` (objet).
- Pour `/latest?from=EUR&to=USD`, `rates` contient la clé `USD` et une valeur numérique positive.
- Pour `/currencies`, la réponse est un objet dont les clés sont des codes de devises et les valeurs des noms sous forme de texte.
- Une devise de base invalide doit produire une réponse d’erreur HTTP non-200 ou une réponse que le test marque explicitement comme invalide; le test n'impose pas un code exact si l'API ne le documente pas clairement.

## Limites et risques

- Service public externe : indisponibilité ou latence possibles.
- Les taux peuvent évoluer selon la date de mise à jour de la source.
- Les tests sont en lecture seule et ne modifient aucune donnée.
- Chaque requête utilise un timeout et un seul nouvel essai au maximum en cas d’erreur réseau/HTTP temporaire.
- Pour rester raisonnable, une exécution limite le nombre d'appels et le runner n'est pas conçu pour être lancé fréquemment.
