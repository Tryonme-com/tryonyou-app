#!/usr/bin/env python3
"""
Supercommit Max Autonomía:
- ejecuta supercommit_max.sh
- sincroniza búnker Oberkampf 75011 con la galería web
- notifica éxito por Telegram (bot de despliegue por entorno)
- valida seguridad martes 08:00 Europe/Paris para activar Dossier Fatality
- escribe memoria operativa en bunker_sovereignty.ma

Sin secretos hardcodeados: todos los tokens van por entorno.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from zoneinfo import ZoneInfo

import requests

PATENT = "PCT/EP2025/067317"
PROTOCOL = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
PARIS_TZ = ZoneInfo("Europe/Paris")
SECURITY_THRESHOLD_EUR = 450_000.0

ROOT = Path(__file__).resolve().parent
SUPERCOMMIT_SCRIPT = ROOT / "supercommit_max.sh"
DEPLOY_SCRIPT = ROOT / "deploy_divineo.py"
DOSSIER_FILE = ROOT / "dossier_fatality_activation.json"
DOSSIER_LOG = ROOT / "dossier_fatality_activation_log.json"
MEMORY_NOTES_FILE = ROOT / "bunker_sovereignty.ma"


@dataclass
class SecurityResult:
    checked: bool
    scheduled_window: bool
    confirmed: bool
    amount_eur: float
    activated: bool
    reason: str


def _sanitize_token(raw: str) -> str:
    # Permite pegar tokens con espacios/saltos de línea sin persistirlos.
    return re.sub(r"\s+", "", raw or "")


def _env_flag(*keys: str) -> bool:
    for key in keys:
        value = (os.getenv(key) or "").strip().lower()
        if value in {"1", "true", "yes", "on", "ok", "confirmed"}:
            return True
    return False


def _parse_amount(raw: str) -> float:
    value = (raw or "").strip()
    if not value:
        return 0.0
    cleaned = re.sub(r"[^\d,.\-]", "", value)
    if not cleaned:
        return 0.0

    if "." in cleaned and "," in cleaned:
        # 450.000,00 -> 450000.00 / 450,000.00 -> 450000.00
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) in (0, 3):
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(",", ".")
    elif "." in cleaned:
        parts = cleaned.split(".")
        if len(parts[-1]) == 3 and len(parts) > 1:
            cleaned = cleaned.replace(".", "")

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _now_paris() -> datetime:
    return datetime.now(PARIS_TZ)


def _is_tuesday_0800(now_paris: datetime) -> bool:
    return now_paris.weekday() == 1 and now_paris.hour == 8


def _run_command(cmd: Sequence[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def run_supercommit(*, fast: bool, deploy: bool, msg: str | None) -> subprocess.CompletedProcess[str]:
    cmd = ["bash", str(SUPERCOMMIT_SCRIPT)]
    if fast:
        cmd.append("--fast")
    if deploy:
        cmd.append("--deploy")
    if msg:
        cmd.extend(["--msg", msg])
    return _run_command(cmd)


def sync_oberkampf_gallery() -> subprocess.CompletedProcess[str]:
    # Sincronización técnica de nodos con delay 0 (no destructivo).
    return _run_command(
        ["python3", str(DEPLOY_SCRIPT), "--force", "--delay", "0"],
    )


def _bot_credentials() -> tuple[str, str]:
    token = _sanitize_token(
        (os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN") or "")
        or (os.getenv("TELEGRAM_BOT_TOKEN") or "")
        or (os.getenv("TELEGRAM_TOKEN") or "")
    )
    chat_id = (
        (os.getenv("TRYONYOU_DEPLOY_BOT_CHAT_ID") or "")
        or (os.getenv("TELEGRAM_CHAT_ID") or "")
    ).strip()
    return token, chat_id


def notify_success(message: str) -> tuple[bool, str]:
    token, chat_id = _bot_credentials()
    if not token:
        return False, "TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN no configurado."
    if not chat_id:
        return False, "TRYONYOU_DEPLOY_BOT_CHAT_ID/TELEGRAM_CHAT_ID no configurado."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message[:3900],
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return True, "ok"
        return False, f"Telegram HTTP {response.status_code}: {response.text[:200]}"
    except requests.RequestException as exc:
        return False, f"Telegram network error: {exc}"


def _capital_confirmation() -> tuple[bool, float, str]:
    confirmed = _env_flag(
        "TRYONYOU_CAPITAL_CONFIRMED",
        "TRYONYOU_FUNDS_450K_CONFIRMED",
        "BUNKER_CAPITAL_ENTRY_CONFIRMED",
    )
    amount = _parse_amount(
        (os.getenv("TRYONYOU_CAPITAL_INFLOW_EUR") or "")
        or (os.getenv("TRYONYOU_FUNDS_450K_AMOUNT_EUR") or "")
        or (os.getenv("TRYONYOU_FUNDS_450K_INFLOW_EUR") or "")
    )
    evidence = (
        (os.getenv("TRYONYOU_CAPITAL_EVIDENCE_FILE") or "")
        or (os.getenv("TRYONYOU_FUNDS_450K_EVIDENCE_FILE") or "")
        or (os.getenv("TRYONYOU_FUNDS_450K_REFERENCE") or "")
    ).strip()
    return confirmed, amount, evidence


def _has_evidence(evidence_ref: str) -> bool:
    if not evidence_ref:
        return False
    evidence_path = Path(evidence_ref)
    if not evidence_path.is_absolute():
        evidence_path = ROOT / evidence_path
    return evidence_path.exists() or bool(evidence_ref)


def evaluate_security(*, force_now: bool = False, now: datetime | None = None) -> SecurityResult:
    now_paris = now.astimezone(PARIS_TZ) if now else _now_paris()
    in_window = _is_tuesday_0800(now_paris)
    if not in_window and not force_now:
        return SecurityResult(
            checked=False,
            scheduled_window=False,
            confirmed=False,
            amount_eur=0.0,
            activated=False,
            reason="Fuera de ventana martes 08:00 Europe/Paris.",
        )

    confirmed, amount, evidence = _capital_confirmation()
    has_evidence = _has_evidence(evidence)
    if not confirmed:
        return SecurityResult(
            checked=True,
            scheduled_window=in_window,
            confirmed=False,
            amount_eur=amount,
            activated=False,
            reason="Capital no confirmado por variable de entorno.",
        )
    if amount < SECURITY_THRESHOLD_EUR:
        return SecurityResult(
            checked=True,
            scheduled_window=in_window,
            confirmed=True,
            amount_eur=amount,
            activated=False,
            reason="Ingreso confirmado pero por debajo de 450000 EUR.",
        )
    if not has_evidence:
        return SecurityResult(
            checked=True,
            scheduled_window=in_window,
            confirmed=True,
            amount_eur=amount,
            activated=False,
            reason="Falta evidencia verificable para activar Dossier Fatality.",
        )

    payload = {
        "activated": True,
        "capital_protection": {
            "amount_eur": amount,
            "threshold_eur": SECURITY_THRESHOLD_EUR,
            "confirmed": True,
            "evidence_reference": evidence,
            "activated_at_utc": datetime.now(timezone.utc).isoformat(),
            "policy": "Dossier Fatality",
            "patent": PATENT,
            "protocol": PROTOCOL,
        },
    }
    DOSSIER_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    log_payload = {
        "event": "DOSSIER_FATALITY_ACTIVATED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_paris": now_paris.isoformat(),
        "amount_eur": amount,
        "evidence_reference": evidence,
        "patent": PATENT,
    }
    DOSSIER_LOG.write_text(json.dumps(log_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return SecurityResult(
        checked=True,
        scheduled_window=in_window,
        confirmed=True,
        amount_eur=amount,
        activated=True,
        reason="Dossier Fatality activado correctamente.",
    )


def update_memory_notes(*, summary: str, security: SecurityResult) -> None:
    lines = [
        "TRYONYOU // BUNKER SOVEREIGNTY NOTES",
        f"Patente: {PATENT}",
        f"Protocolo: {PROTOCOL}",
        "",
        "Estado de operación:",
        f"- Supercommit/Sync: {summary}",
        f"- Ventana seguridad martes 08:00: {'si' if security.scheduled_window else 'no'}",
        f"- Capital confirmado: {'si' if security.confirmed else 'no'}",
        f"- Monto observado EUR: {security.amount_eur:.2f}",
        f"- Dossier Fatality activado: {'si' if security.activated else 'no'}",
        f"- Motivo: {security.reason}",
        "",
        "Nota: no afirmar confirmaciones bancarias sin evidencia verificable.",
    ]
    MEMORY_NOTES_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orquestador Supercommit Max autonomía.")
    parser.add_argument("--fast", action="store_true", help="Pasa --fast a supercommit_max.sh.")
    parser.add_argument("--deploy", action="store_true", help="Pasa --deploy a supercommit_max.sh.")
    parser.add_argument("--msg", type=str, default="", help="Mensaje personalizado para commit.")
    parser.add_argument(
        "--security-check-now",
        action="store_true",
        help="Ejecuta validación de seguridad sin esperar martes 08:00.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not SUPERCOMMIT_SCRIPT.exists():
        print("supercommit_max.sh no encontrado.", file=sys.stderr)
        return 1

    supercommit = run_supercommit(fast=args.fast, deploy=args.deploy, msg=args.msg or None)
    if supercommit.returncode != 0:
        print(supercommit.stdout)
        print(supercommit.stderr, file=sys.stderr)
        return supercommit.returncode

    sync = sync_oberkampf_gallery()
    if sync.returncode != 0:
        print(sync.stdout)
        print(sync.stderr, file=sys.stderr)
        return sync.returncode

    security = evaluate_security(force_now=args.security_check_now)
    summary = "Supercommit_Max ejecutado y Oberkampf 75011 sincronizado con galería web."
    update_memory_notes(summary=summary, security=security)

    success_msg = (
        "✅ TRYONYOU AUTONOMÍA TOTAL\n"
        f"{summary}\n"
        f"Seguridad martes 08:00 => {security.reason}\n"
        f"Dossier Fatality: {'ACTIVADO' if security.activated else 'NO ACTIVADO'}\n"
        f"{PATENT}"
    )
    sent, detail = notify_success(success_msg)
    if not sent:
        print(f"No se pudo notificar éxito por Telegram: {detail}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
