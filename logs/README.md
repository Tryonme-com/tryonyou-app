# logs/

Fichiers générés au runtime (ne pas committer les données sensibles) :

- `ip_access.jsonl` — une ligne JSON par accès si `BUNKER_STEALTH_TOTAL` est actif.
- `IP_WATCH.md` — lignes ajoutées pour les accès refusés (kill-switch inventaire, etc.).
- `LAFAYETTE_TTC_MONITOR.md` — si `LAFAYETTE_TTC_MONITOR_LOG=1` et abono **9 000 € TTC** validé (env), une ligne **UNLOCK** / jour UTC lors d’un appel réussi à `/api/v1/inventory/status` ou `/api/v1/mirror/snap` (indicateur runtime ; FS serverless souvent éphémère).
- `SISTEMA_SUSPENDIDO.jsonl` — événements blackout (503 Lafayette / inventaire verrouillé) si `BUNKER_BLACKOUT_MODE=1`.

Créés par `api/stealth_bunker.py` / `api/index.py`.
