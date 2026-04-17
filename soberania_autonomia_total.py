"""
Orquestador de autonomía soberana TryOnYou.

Objetivos:
1) Ejecutar Supercommit_Max (sincronización búnker Oberkampf 75011 <-> galería web).
2) Notificar cada éxito mediante el bot @tryonyou_deploy_bot.
3) Verificar martes 08:00 (Europe/Paris) la entrada de 450.000 € y activar Dossier Fatality.

Secretos:
- Nunca hardcodear tokens. Usar variables de entorno.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PATENT = "PCT/EP2025/067317"
FOUNDER_PROTOCOL = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
BOT_HANDLE = "@tryonyou_deploy_bot"
EXPECTED_CAPITAL_EUR = Decimal("450000")
PARIS_TZ = ZoneInfo("Europe/Paris")


def _to_decimal(value: str) -> Decimal:
    normalized = value.strip().replace(".", "").replace(",", ".")
    return Decimal(normalized)


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class CapitalCheck:
    confirmed: bool
    amount: Decimal
    source: str
    detail: str


class TryOnYouDeployNotifier:
    def __init__(self) -> None:
        raw_token = (
            os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "")
            or os.environ.get("TELEGRAM_BOT_TOKEN", "")
            or os.environ.get("TELEGRAM_TOKEN", "")
        )
        self.token = "".join(raw_token.split())
        self.chat_id = (
            os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "")
            or os.environ.get("TELEGRAM_CHAT_ID", "")
        ).strip()

    def _call(self, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("Token de Telegram ausente en entorno.")
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        data = None
        if payload:
            data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
        with urllib.request.urlopen(req, timeout=20) as res:
            body = res.read().decode("utf-8")
        parsed = json.loads(body)
        if not parsed.get("ok"):
            raise RuntimeError(f"Telegram API error: {parsed}")
        return parsed

    def _discover_chat_id(self) -> str:
        result = self._call("getUpdates", {"limit": "25"})
        updates = result.get("result") or []
        for item in reversed(updates):
            for field in ("message", "edited_message", "channel_post"):
                block = item.get(field) or {}
                chat = block.get("chat") or {}
                chat_id = chat.get("id")
                if chat_id is not None:
                    return str(chat_id)
        raise RuntimeError(
            "No se pudo detectar chat_id con getUpdates. "
            "Define TRYONYOU_DEPLOY_CHAT_ID o TELEGRAM_CHAT_ID."
        )

    def success(self, step: str, detail: str) -> bool:
        if not self.token:
            print("ℹ️ Telegram omitido: falta TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN.")
            return False
        chat_id = self.chat_id
        if not chat_id:
            try:
                chat_id = self._discover_chat_id()
            except Exception as exc:
                print(f"⚠️ Telegram omitido ({step}): {exc}", file=sys.stderr)
                return False
        text = (
            f"{BOT_HANDLE} ✅ Éxito: {step}\n"
            f"{detail}\n"
            f"Patente: {PATENT}\n"
            f"{FOUNDER_PROTOCOL}"
        )
        try:
            self._call("sendMessage", {"chat_id": chat_id, "text": text})
            return True
        except Exception as exc:
            print(f"⚠️ No se pudo notificar Telegram ({step}): {exc}", file=sys.stderr)
            return False


class SoberaniaAutonomia:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.notifier = TryOnYouDeployNotifier()

    def _run(self, args: list[str]) -> int:
        return subprocess.run(args, cwd=self.root, check=False).returncode

    def check_bash_quality(self) -> bool:
        scripts = [
            "supercommit_max.sh",
            "percommit_max.sh",
            "TRYONYOU_SUPERCOMMIT_MAX.sh",
        ]
        for script in scripts:
            path = self.root / script
            if not path.is_file():
                continue
            rc = self._run(["bash", "-n", script])
            if rc != 0:
                raise RuntimeError(f"Error de sintaxis Bash detectado en {script}")
        self.notifier.success(
            "Calidad Bash 10/10",
            "Galería validada sin errores de sintaxis Bash.",
        )
        return True

    def run_supercommit_max(self, message: str) -> None:
        script = self.root / "supercommit_max.sh"
        if not script.is_file():
            raise FileNotFoundError("No existe supercommit_max.sh en la raíz.")
        rc = self._run(["bash", "supercommit_max.sh", message])
        if rc != 0:
            raise RuntimeError(f"Supercommit_Max falló con código {rc}")
        self.notifier.success(
            "Supercommit_Max",
            "Sincronización Oberkampf 75011 -> galería web completada.",
        )

    def _is_tuesday_8am(self, now: datetime) -> bool:
        return now.weekday() == 1 and now.hour == 8

    def _read_capital_from_env(self) -> CapitalCheck | None:
        raw = os.environ.get("SOVEREIGN_CONFIRMED_CAPITAL_EUR", "").strip()
        if not raw:
            return None
        try:
            amount = _to_decimal(raw)
        except (InvalidOperation, ValueError):
            return CapitalCheck(False, Decimal("0"), "env", "Valor inválido en SOVEREIGN_CONFIRMED_CAPITAL_EUR")
        confirmed = amount >= EXPECTED_CAPITAL_EUR
        detail = f"Confirmación por entorno: {amount} EUR"
        return CapitalCheck(confirmed, amount, "env", detail)

    def _read_capital_from_csv(self) -> CapitalCheck:
        ledger_path = Path(
            os.environ.get("SOVEREIGN_LEDGER_PATH", str(self.root / "registro_pagos_hoy.csv"))
        )
        if not ledger_path.is_file():
            return CapitalCheck(False, Decimal("0"), "csv", f"No existe {ledger_path.name}")
        total = Decimal("0")
        with ledger_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                status = (row.get("estado") or "").strip().upper()
                if status != "CONFIRMADO":
                    continue
                raw_amount = (row.get("importe_eur") or "").strip()
                if not raw_amount:
                    continue
                try:
                    total += _to_decimal(raw_amount)
                except (InvalidOperation, ValueError):
                    continue
        confirmed = total >= EXPECTED_CAPITAL_EUR
        return CapitalCheck(
            confirmed,
            total,
            "csv",
            f"Suma CONFIRMADO en {ledger_path.name}: {total} EUR",
        )

    def verify_capital_entry(self) -> CapitalCheck:
        from_env = self._read_capital_from_env()
        if from_env is not None:
            return from_env
        return self._read_capital_from_csv()

    def activate_dossier_fatality(self, amount: Decimal, source: str) -> Path:
        dossier = self.root / "dossier_fatality.json"
        if not dossier.is_file():
            raise FileNotFoundError("No se encontró dossier_fatality.json")
        dossier_bytes = dossier.read_bytes()
        checksum = hashlib.sha256(dossier_bytes).hexdigest()
        logs_dir = self.root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        target = logs_dir / "dossier_fatality_activation.json"
        payload = {
            "event": "DOSSIER_FATALITY_ACTIVATED",
            "timestamp_paris": datetime.now(PARIS_TZ).isoformat(timespec="seconds"),
            "expected_eur": str(EXPECTED_CAPITAL_EUR),
            "confirmed_eur": str(amount),
            "source": source,
            "dossier_file": "dossier_fatality.json",
            "dossier_sha256": checksum,
            "patent": PATENT,
            "protocol": FOUNDER_PROTOCOL,
        }
        target.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        self.notifier.success(
            "Dossier Fatality activado",
            f"Capital protegido: {amount} EUR ({source}).",
        )
        return target

    def run_security_gate(self) -> int:
        now = datetime.now(PARIS_TZ)
        if not self._is_tuesday_8am(now) and not _truthy("SOVEREIGN_FORCE_SECURITY_CHECK"):
            print(
                "ℹ️ Seguridad programada: espera martes 08:00 Europe/Paris "
                "(o usa SOVEREIGN_FORCE_SECURITY_CHECK=1)."
            )
            return 0

        check = self.verify_capital_entry()
        print(f"🔎 Seguridad 08:00 — {check.detail}")
        if not check.confirmed:
            raise RuntimeError(
                f"Capital insuficiente para activar Fatality ({check.amount} EUR / {EXPECTED_CAPITAL_EUR} EUR)."
            )
        target = self.activate_dossier_fatality(check.amount, check.source)
        print(f"✅ Dossier Fatality activo: {target}")
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autonomía soberana TryOnYou")
    parser.add_argument(
        "--skip-supercommit",
        action="store_true",
        help="No ejecutar Supercommit_Max.",
    )
    parser.add_argument(
        "--skip-security",
        action="store_true",
        help="No ejecutar compuerta de seguridad martes 08:00.",
    )
    parser.add_argument(
        "--commit-message",
        default="chore: Supercommit_Max soberano Oberkampf 75011",
        help="Mensaje base para Supercommit_Max (sellos obligatorios se añaden automáticamente).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    runner = SoberaniaAutonomia(root)

    runner.check_bash_quality()
    if not args.skip_supercommit:
        runner.run_supercommit_max(args.commit_message)
    if not args.skip_security:
        runner.run_security_gate()
    runner.notifier.success(
        "Autonomía total completada",
        "Flujo de despliegue y seguridad ejecutado con éxito.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
