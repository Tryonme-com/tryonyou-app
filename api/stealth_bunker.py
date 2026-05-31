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


# Facture 2026-04-01-001 : 7 500 € HT + TVA 20 % = 9 000 € TTC (kill-switch production).
_EXPECTED_LAFAYETTE_TTC_EUR = 9000.0


def _parse_euro_amount(raw: str) -> float | None:
    s = (raw or "").strip().replace(" ", "").replace("€", "").replace("\u00a0", "")
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _payment_ttc_gate_satisfied() -> bool:
    """True si l'ingreso íntegre facture maestra (9 000 € TTC) est confirmé."""
    flag = os.environ.get("LAFAYETTE_SETUP_FEE_TTC_VALIDATED", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    for key in ("LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR", "LAFAYETTE_PAYMENT_TTC_EUR"):
        v = _parse_euro_amount(os.environ.get(key, "") or "")
        if v is not None and v + 1e-9 >= _EXPECTED_LAFAYETTE_TTC_EUR:
            return True
    return False


def bunker_blackout_mode() -> bool:
    return os.environ.get("BUNKER_BLACKOUT_MODE", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def lafayette_ip_matches(handler: BaseHTTPRequestHandler) -> bool:
    if os.environ.get("LAFAYETTE_BLACKOUT_ALL_IPS_AS_LAFAYETTE", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        return True
    prefixes = [
        p.strip()
        for p in os.environ.get("LAFAYETTE_IP_PREFIXES", "").split(",")
        if p.strip()
    ]
    if not prefixes:
        return False
    ip = client_ip(handler)
    return any(ip.startswith(p) for p in prefixes)


def append_sistema_suspendido_log(ip: str, detail: str) -> None:
    path = os.path.join(_logs_dir(), "SISTEMA_SUSPENDIDO.jsonl")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = json.dumps(
        {"ts": ts, "ip": ip, "event": "sistema_suspendido", "detail": detail[:200]},
        ensure_ascii=False,
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


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
    Déblocage inventaire (310 refs) — facture F-2026-001 : **9 000 € TTC** sur IBAN BNP.

    Toute levée exige le gate TTC (sauf LAFAYETTE_ALLOW_HASH_UNLOCK_WITHOUT_TTC pour hash atelier).
    """
    ttc_ok = _payment_ttc_gate_satisfied()

    fee_paid_flag = (
        os.environ.get("LAFAYETTE_SETUP_FEE_STATUS", "").strip().upper() == "PAID"
    )
    if fee_paid_flag and ttc_ok:
        return True

    iban_confirm = (
        os.environ.get("LAFAYETTE_BNP_IBAN_TTC_VALIDATED", "").strip().lower()
        or os.environ.get("LAFAYETTE_BNP_IBAN_7500_VALIDATED", "").strip().lower()
    )
    if iban_confirm in ("1", "true", "yes", "on") and ttc_ok:
        return True

    submitted_iban = _normalize_iban(
        os.environ.get("LAFAYETTE_SETUP_PAYMENT_IBAN", "").strip()
    )
    expected_iban = _expected_iban_for_unlock()
    if (
        submitted_iban
        and expected_iban
        and submitted_iban == expected_iban
      and ttc_ok
    ):
        return True

    flag = os.environ.get("SETUP_FEE_7500_VALIDATED", "").strip().lower()
    if flag in ("1", "true", "yes", "on") and ttc_ok:
        return True
    expected = os.environ.get("LAFAYETTE_SETUP_EXPECTED_HASH", "").strip()
    provided = os.environ.get("LAFAYETTE_SETUP_PAYMENT_HASH", "").strip()
    if expected and provided and provided.lower() == expected.lower():
        if (
            os.environ.get("LAFAYETTE_ALLOW_HASH_UNLOCK_WITHOUT_TTC", "")
            .strip()
            .lower()
            in ("1", "true", "yes", "on")
        ):
            return True
        return ttc_ok
    secret = os.environ.get("LAFAYETTE_SETUP_UNLOCK_SECRET", "").strip()
    if secret and provided:
        calc = hashlib.sha256(f"{secret}:7500:EUR".encode("utf-8")).hexdigest()
        if provided.lower() == calc.lower():
            if (
                os.environ.get("LAFAYETTE_ALLOW_HASH_UNLOCK_WITHOUT_TTC", "")
                .strip()
                .lower()
                in ("1", "true", "yes", "on")
            ):
                return True
            return ttc_ok
    return False


def inventory_collection_path_forbidden(url_path: str) -> bool:
    if inventory_references_unlocked():
        return False
    p = (url_path or "").replace("\\", "/").lower()
    if "current_inventory" in p:
        return True
    if "inventory_engine" in p:
        return True
    seg = p.strip("/").split("/")
    if len(seg) >= 2 and seg[0] == "api" and "inventory" in p:
        return True
    return False


def maybe_log_ttc_unlock_event(handler: BaseHTTPRequestHandler | None = None) -> None:
    """
    Si LAFAYETTE_TTC_MONITOR_LOG=1 et moteur débloqué : une ligne / jour UTC dans
    logs/LAFAYETTE_TTC_MONITOR.md (détection abono 9 000 € TTC côté env).
    Sur serverless, FS souvent éphémère — traiter comme indicateur, pas preuve comptable.
    """
    if not inventory_references_unlocked():
        return
    if os.environ.get("LAFAYETTE_TTC_MONITOR_LOG", "").strip().lower() not in (
        "1",
        "true",
        "yes",
        "on",
    ):
        return
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join(_logs_dir(), "LAFAYETTE_TTC_MONITOR.md")
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                tail = f.read()[-600:]
            if day in tail and "UNLOCK" in tail:
                return
        except OSError:
            pass
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ip = client_ip(handler) if handler is not None else "—"
    row = (
        f"| {ts} | **UNLOCK** | Gate TTC 9 000 € (F-2026-001) — moteur 310 refs · IP `{ip}` |\n"
    )
    if not os.path.isfile(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                "# LAFAYETTE TTC — monitor (abono 9 000 € TTC)\n\n"
                "| UTC | État | Détail |\n|-----|------|--------|\n"
            )
    with open(path, "a", encoding="utf-8") as f:
        f.write(row)


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
            "Colonne *outcome* : `inventory_locked` = kill-switch facture 9 000 € TTC / IBAN "
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
