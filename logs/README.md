# logs/

Fichiers générés au runtime (ne pas committer les données sensibles) :

- `ip_access.jsonl` — une ligne JSON par accès si `BUNKER_STEALTH_TOTAL` est actif.
- `IP_WATCH.md` — lignes ajoutées pour les accès refusés (kill-switch inventaire, etc.).

Créés par `api/stealth_bunker.py` lors des requêtes traitées par `api/index.py`.
