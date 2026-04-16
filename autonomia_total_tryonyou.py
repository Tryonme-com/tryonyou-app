#!/usr/bin/env python3
"""Autonomia total TryOnYou: Supercommit + sync + Dossier Fatality.

Objetivos:
1) Ejecutar Supercommit_Max.
2) Sincronizar bunker Oberkampf (75011) con galeria web.
3) En ventana de seguridad (martes 08:00), validar senal de 450000 EUR
   y activar Dossier Fatality para proteger capital.
4) Crear/actualizar Memory Notes en bunker_sovereignty.ma.

Secretos solo por entorno. Nunca hardcodear tokens en el codigo.
Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

PATENT = "PCT/EP2025/067317"
SOVEREIGN_PROTOCOL = "Bajo Protocolo de Soberania V10 - Founder: Ruben"
TARGET_AMOUNT_EUR = 450000
DEFAULT_MEMORY_NOTES = "bunker_sovereignty.ma"

ROOT = Path(__file__).resolve().parent
SUPERCOMMIT = ROOT / "supercommit_max.sh"
DOSSIER = ROOT / "dossier_fatality.json"


def _truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on", "si", "ok"}


def in_security_window(now: datetime | None = None, tolerance_minutes: int = 10) -> bool:
    """Return True for Tuesday 08:00 within a tolerance window."""
    ref = now or datetime.now()
    return ref.weekday() == 1 and ref.hour == 8 and 0 <= ref.minute <= tolerance_minutes


def _extract_amount_tokens(text: str) -> set[str]:
    return set(re.findall(r"\d[\d\.\,\s]*", text))


def detect_funds_confirmation() -> tuple[bool, str]:
    """Detect operational confirmation for 450.000 EUR.

    Sources:
    - TRYONYOU_FUNDS_450K_CONFIRMED=1
    - TRYONYOU_FUNDS_450K_EVIDENCE_FILE=/path/proof.txt (contains amount token)
    """
    if _truthy(os.getenv("TRYONYOU_FUNDS_450K_CONFIRMED")):
        ref = os.getenv("TRYONYOU_FUNDS_450K_REFERENCE", "").strip() or "env_flag"
        return True, f"confirmed_by_env:{ref}"

    evidence = (os.getenv("TRYONYOU_FUNDS_450K_EVIDENCE_FILE") or "").strip()
    if evidence:
        p = Path(evidence)
        if p.is_file():
            content = p.read_text(encoding="utf-8", errors="ignore")
            tokens = _extract_amount_tokens(content)
            if any(
                t.replace(" ", "") in {"450000", "450.000", "450,000", "450000,00"}
                for t in tokens
            ):
                return True, f"confirmed_by_file:{p.name}"
            return False, f"evidence_file_without_amount:{p.name}"
        return False, f"evidence_file_not_found:{p}"

    return False, "missing_confirmation_signal"


@dataclass
class DeployBot:
    token: str
    chat_id: str
    dry_run: bool = False

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str) -> bool:
        if not self.enabled:
            return False
        if self.dry_run:
            print(f"[dry-run telegram] {text}")
            return True
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload: dict[str, Any] = {"chat_id": self.chat_id, "text": text}
        try:
            r = requests.post(url, json=payload, timeout=20)
            r.raise_for_status()
            return True
        except requests.RequestException as exc:
            print(f"WARN Telegram no disponible: {exc}", file=sys.stderr)
            return False


def run_supercommit(*, fast: bool, deploy: bool, custom_msg: str | None) -> None:
    if not SUPERCOMMIT.is_file():
        raise FileNotFoundError(f"No existe {SUPERCOMMIT}")
    cmd = ["bash", str(SUPERCOMMIT)]
    if fast:
        cmd.append("--fast")
    if deploy:
        cmd.append("--deploy")
    if custom_msg:
        cmd.extend(["--msg", custom_msg])
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def sync_oberkampf_75011() -> dict[str, object]:
    from deploy_divineo import deploy_divineo

    return deploy_divineo(
        nodes=("Oberkampf-75011", "Galeria-Web"),
        delay_seconds=0.0,
        force=True,
    )


def activate_dossier_fatality(
    *, force: bool, now: datetime | None = None, tolerance_minutes: int = 10
) -> dict[str, object]:
    data: dict[str, Any] = {}
    if DOSSIER.is_file():
        data = json.loads(DOSSIER.read_text(encoding="utf-8"))

    current = now or datetime.now()
    window_ok = in_security_window(current, tolerance_minutes=tolerance_minutes)
    confirmed, source = detect_funds_confirmation()

    if force:
        status = "active" if confirmed else "pending_confirmation"
    elif not window_ok:
        status = "scheduled_wait"
    else:
        status = "active" if confirmed else "pending_confirmation"

    protocol_block: dict[str, Any] = {
        "target_amount_eur": TARGET_AMOUNT_EUR,
        "confirmed": confirmed,
        "confirmation_source": source,
        "status": status,
        "window_ok": window_ok,
        "timestamp": current.isoformat(timespec="seconds"),
    }
    data["capital_protection"] = protocol_block
    DOSSIER.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return protocol_block


def write_memory_notes(path: Path) -> None:
    notes = (
        "TRYONYOU MEMORY NOTES\n"
        "=====================\n"
        "- Bot de despliegue: @tryonyou_deploy_bot via entorno "
        "(TRYONYOU_DEPLOY_BOT_TOKEN + TRYONYOU_DEPLOY_BOT_CHAT_ID).\n"
        "- Supercommit_Max ejecutado para consolidacion tecnica.\n"
        "- Sincronizacion objetivo: Oberkampf 75011 <-> galeria web.\n"
        "- Dossier Fatality: activar solo con senal verificable de 450000 EUR "
        "en martes 08:00 (o force explicito).\n"
        "- Nunca afirmar confirmacion bancaria sin evidencia operativa.\n"
        f"- Patente: {PATENT}. {SOVEREIGN_PROTOCOL}\n"
    )
    path.write_text(notes, encoding="utf-8")


def _read_bot_config() -> tuple[str, str]:
    token = (
        os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
    )
    chat = (
        os.getenv("TRYONYOU_DEPLOY_BOT_CHAT_ID", "").strip()
        or os.getenv("TELEGRAM_CHAT_ID", "").strip()
    )
    return token, chat


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autonomia total de despliegue TryOnYou.")
    parser.add_argument("--skip-supercommit", action="store_true")
    parser.add_argument("--supercommit-fast", action="store_true")
    parser.add_argument("--supercommit-deploy", action="store_true")
    parser.add_argument("--supercommit-msg", default="")
    parser.add_argument("--force-security-check", action="store_true")
    parser.add_argument("--security-window-minutes", type=int, default=10)
    parser.add_argument("--memory-notes-path", default=DEFAULT_MEMORY_NOTES)
    parser.add_argument("--allow-missing-bot", action="store_true")
    parser.add_argument("--dry-run-telegram", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    token, chat = _read_bot_config()
    bot = DeployBot(token=token, chat_id=chat, dry_run=args.dry_run_telegram)

    if not bot.enabled and not args.allow_missing_bot:
        print(
            "ERROR: Falta configuracion del bot. Define TRYONYOU_DEPLOY_BOT_TOKEN "
            "y TRYONYOU_DEPLOY_BOT_CHAT_ID (o TELEGRAM_*).",
            file=sys.stderr,
        )
        return 2

    bot.send("@tryonyou_deploy_bot inicio autonomia total TryOnYou: protocolo en ejecucion.")
    try:
        if not args.skip_supercommit:
            run_supercommit(
                fast=args.supercommit_fast,
                deploy=args.supercommit_deploy,
                custom_msg=args.supercommit_msg.strip() or None,
            )
            bot.send("@tryonyou_deploy_bot OK: Supercommit_Max ejecutado con exito.")

        sync_result = sync_oberkampf_75011()
        if not bool(sync_result.get("deploy", False)):
            raise RuntimeError("Sincronizacion Oberkampf 75011 no completada.")
        bot.send(
            "@tryonyou_deploy_bot OK: sincronizacion Oberkampf 75011 con galeria web completada."
        )

        protection = activate_dossier_fatality(
            force=args.force_security_check,
            tolerance_minutes=max(0, args.security_window_minutes),
        )
        if protection["status"] == "active":
            bot.send("@tryonyou_deploy_bot OK: Dossier Fatality ACTIVADO para proteccion de capital.")
        elif protection["status"] == "pending_confirmation":
            bot.send("@tryonyou_deploy_bot ALERTA: Dossier Fatality pendiente, falta confirmacion de 450000 EUR.")
        else:
            bot.send("@tryonyou_deploy_bot INFO: ventana de seguridad fuera de rango, dossier en espera.")

        memory_path = (ROOT / args.memory_notes_path).resolve()
        write_memory_notes(memory_path)
        bot.send("@tryonyou_deploy_bot OK: Memory Notes actualizado en bunker_sovereignty.ma.")
        print("Autonomia total completada.")
        return 0
    except Exception as exc:
        bot.send(f"@tryonyou_deploy_bot ERROR en autonomia TryOnYou: {exc}")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
