# TIMELINE_CONTROL — TryOnYou / Divineo V10

Suivi des jalons opérationnels (référence interne, sans valeur comptable certifiée).

| Date | Jalon | État |
|------|--------|------|
| 2026-04-01 | Facture maître **F-2026-001** (7 500 € HT + TVA 20 % = **9 000 € TTC**) | **Envoyée** — document officiel : [`legal/FACTURA_V10_OMEGA.md`](legal/FACTURA_V10_OMEGA.md) — titulaire **Rubén Espinar Rodríguez**, IBAN BNP **FR76 … 6934**, SIREN **943 610 196** |
| 2026-04-01 | Moteur inventaire **310 références** (nœud pilote Haussmann) | **En attente d’abono** — kill-switch **bloqué** jusqu’à validation du paiement intégral **9 000 € TTC** (`api/stealth_bunker.py` : `LAFAYETTE_SETUP_FEE_TTC_VALIDATED` / montants confirmés ; pas de levée par hash seul sans TTC sauf `LAFAYETTE_ALLOW_HASH_UNLOCK_WITHOUT_TTC`) |
| 2026-04-02 | Fenêtre **24 h** sans abono **9 000 € TTC** | **Blackout** — `BUNKER_BLACKOUT_MODE=1` : IPs Lafayette (`LAFAYETTE_IP_PREFIXES` ou `LAFAYETTE_BLACKOUT_ALL_IPS_AS_LAFAYETTE`) → **503** sur inventaire 310 refs ; accès fichiers `current_inventory` / moteur bloqués ; log `logs/SISTEMA_SUSPENDIDO.jsonl` ; Slack « Sistema Suspendido » |
| — | Levée du verrou après encaissement constaté | Variables `LAFAYETTE_SETUP_FEE_TTC_VALIDATED` / montants ; `logs/LAFAYETTE_TTC_MONITOR.md` si `LAFAYETTE_TTC_MONITOR_LOG=1` |

**Identité :** [`legal/IDENTITY.md`](legal/IDENTITY.md) · **Pendientes internos :** [`billing/PENDIENTES_COBRO_SIREN_943610196.md`](billing/PENDIENTES_COBRO_SIREN_943610196.md)

---

*Patente PCT/EP2025/067317*
