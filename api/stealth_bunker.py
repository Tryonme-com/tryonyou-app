"""
Stealth bunker — journal d'accès (75001), kill-switch inventaire 310 références.

Ne pas versionner logs/*.jsonl ni logs/IP_WATCH.md (données personnelles / IP).
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _logs_dir() -> str:
    d = os.path.join(_project_root(), "logs")
    os.makedirs(d, exist_ok=True)
    return d


def bunker_stealth_enabled() -> bool:
    v = os.environ.get("BUNKER_STEALTH_TOTAL", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _normalize_iban(raw: str) -> str:
    """IBAN sans espaces, en majuscules (comparaison stricte)."""
    return "".join(c for c in (raw or "").strip().upper() if c.isalnum())


# Référence unique avec /legal/IDENTITY.md (fallback si LAFAYETTE_EXPECTED_IBAN absent).
_CANONICAL_LAFAYETTE_IBAN_FR = _normalize_iban(
    "FR76 3000 4031 8900 0058 4046 934"
)


def _expected_iban_for_unlock() -> str:
    env = os.environ.get("LAFAYETTE_EXPECTED_IBAN", "").strip()
    if env:
        return _normalize_iban(env)
    return _CANONICAL_LAFAYETTE_IBAN_FR


def client_ip(handler: BaseHTTPRequestHandler) -> str:
    xff = handler.headers.get("X-Forwarded-For", "") or ""
    if xff.strip():
        return xff.split(",")[0].strip()[:128]
    xri = (handler.headers.get("X-Real-IP", "") or "").strip()
    if xri:
        return xri[:128]
    try:
        return (handler.client_address[0] or "unknown")[:128]
    except (AttributeError, IndexError, TypeError):
        return "unknown"


def inventory_references_unlocked() -> bool:
    """
    Déblocage inventaire (310 refs) — liquidation setup 7 500 €, priorité validation IBAN BNP.

    - IBAN : LAFAYETTE_BNP_IBAN_7500_VALIDATED=1 (contrôle manuel virement reçu)
      ou LAFAYETTE_SETUP_PAYMENT_IBAN normalisé == LAFAYETTE_EXPECTED_IBAN (fallback : IDENTITY.md).
    - Secours : SETUP_FEE_7500_VALIDATED / hash (intégration historique).
    """
    fee_paid_flag = (
        os.environ.get("LAFAYETTE_SETUP_FEE_STATUS", "").strip().upper() == "PAID"
    )
    if fee_paid_flag:
        return True

    iban_confirm = os.environ.get("LAFAYETTE_BNP_IBAN_7500_VALIDATED", "").strip().lower()
    if iban_confirm in ("1", "true", "yes", "on"):
        return True

    submitted_iban = _normalize_iban(
        os.environ.get("LAFAYETTE_SETUP_PAYMENT_IBAN", "").strip()
    )
    expected_iban = _expected_iban_for_unlock()
    if submitted_iban and expected_iban and submitted_iban == expected_iban:
        return True

    flag = os.environ.get("SETUP_FEE_7500_VALIDATED", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    expected = os.environ.get("LAFAYETTE_SETUP_EXPECTED_HASH", "").strip()
    provided = os.environ.get("LAFAYETTE_SETUP_PAYMENT_HASH", "").strip()
    if expected and provided and provided.lower() == expected.lower():
        return True
    secret = os.environ.get("LAFAYETTE_SETUP_UNLOCK_SECRET", "").strip()
    if secret and provided:
        calc = hashlib.sha256(f"{secret}:7500:EUR".encode("utf-8")).hexdigest()
        if provided.lower() == calc.lower():
            return True
    return False


def _append_jsonl(entry: dict[str, Any]) -> None:
    path = os.path.join(_logs_dir(), "ip_access.jsonl")
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _append_ip_watch_row(
    ts: str,
    ip: str,
    method: str,
    path_s: str,
    outcome: str,
    detail: str,
) -> None:
    md_path = os.path.join(_logs_dir(), "IP_WATCH.md")
    row = f"| {ts} | `{ip}` | {method} | `{path_s}` | **{outcome}** | {detail} |\n"
    if not os.path.isfile(md_path):
        header = (
            "# IP_WATCH — accès bunker (généré automatiquement)\n\n"
            "Colonne *outcome* : `inventory_locked` = kill-switch setup 7 500 € "
            "non validé ; `stealth` = page masquée servie.\n\n"
            "| UTC | IP | Méthode | Chemin | Outcome | Détail |\n"
            "|-----|----|---------|--------|---------|--------|\n"
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(header)
    with open(md_path, "a", encoding="utf-8") as f:
        f.write(row)


FAILED_OUTCOMES = frozenset({"inventory_locked", "access_denied"})


def log_bunker_access(
    handler: BaseHTTPRequestHandler,
    method: str,
    path_s: str,
    outcome: str,
    detail: str = "",
    http_status: int = 200,
) -> None:
    """Si stealth actif : trace chaque accès ; les échecs alimentent IP_WATCH.md."""
    if not bunker_stealth_enabled():
        return
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ip = client_ip(handler)
    entry = {
        "ts": ts,
        "ip": ip,
        "method": method,
        "path": path_s[:512],
        "outcome": outcome,
        "detail": detail[:300],
        "http_status": http_status,
    }
    _append_jsonl(entry)
    if outcome in FAILED_OUTCOMES or http_status >= 400:
        _append_ip_watch_row(ts, ip, method, path_s, outcome, detail or "—")


def stealth_html_body() -> bytes:
    """Plein écran noir, marque SACMUSEUM, message 75001 (aucune SPA)."""
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>SACMUSEUM — 75001</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      min-height: 100vh;
      background: #000;
      color: #C5A46D;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-family: Georgia, "Times New Roman", serif;
      padding: 2rem;
      text-align: center;
    }
    .logo {
      font-size: clamp(1.5rem, 5vw, 2.25rem);
      letter-spacing: 0.4em;
      font-weight: 600;
      margin-bottom: 2.5rem;
      text-transform: uppercase;
    }
    .line {
      max-width: 28rem;
      font-size: 1.05rem;
      line-height: 1.65;
      letter-spacing: 0.06em;
    }
  </style>
</head>
<body>
  <div class="logo">SACMUSEUM</div>
  <p class="line">L'accès à la rareté est un privilège. Contactez le 75001.</p>
</body>
</html>
"""
    return html.encode("utf-8")
