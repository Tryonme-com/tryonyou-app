#!/usr/bin/env python3
"""Orquestador de autonomía total para TryOnYou (modo seguro).

Este módulo implementa una versión segura de la solicitud operacional:
- Notificaciones de éxito vía Telegram usando variables de entorno.
- Ejecución de Supercommit_Max para sincronización técnica.
- Verificación programada (martes 08:00) de evidencia de capital.
- Activación de Dossier Fatality en modo de protección documental.

No ejecuta transferencias, cobros ni acciones financieras reales.
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
from typing import Any, Callable

import requests

PATENTE = "PCT/EP2025/067317"
SOVEREIGN_PROTOCOL = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
EXPECTED_CAPITAL_EUR = 450000
DEPLOY_BOT_USERNAME = "@tryonyou_deploy_bot"
DEFAULT_MEMORY_FILE = "bunker_sovereignty.ma"
DEFAULT_EVIDENCE_FILE = "capital_entry_evidence.json"
DOSSIER_LOG_FILE = Path("logs/dossier_fatality_activation.json")


@dataclass(frozen=True)
class CapitalCheckResult:
    ok: bool
    message: str


def parse_eur_amount(value: Any) -> int:
    """Convierte cantidades tipo 450000 / '450.000€' a entero en EUR."""
    if isinstance(value, bool):
        raise ValueError("Valor booleano no válido como cantidad.")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if not isinstance(value, str):
        raise ValueError(f"Tipo no soportado para cantidad: {type(value)!r}")

    cleaned = value.strip()
    cleaned = cleaned.replace("EUR", "").replace("€", "")
    cleaned = cleaned.replace(" ", "").replace("_", "")

    # Normaliza separadores para soportar:
    # 450.000,00 | 450,000.00 | 450.000 | 450,000 | 450000
    if "," in cleaned and "." in cleaned:
        last_comma = cleaned.rfind(",")
        last_dot = cleaned.rfind(".")
        decimal_sep = "," if last_comma > last_dot else "."
        thousand_sep = "." if decimal_sep == "," else ","
        cleaned = cleaned.replace(thousand_sep, "")
        cleaned = cleaned.split(decimal_sep, maxsplit=1)[0]
    elif "," in cleaned or "." in cleaned:
        sep = "," if "," in cleaned else "."
        parts = cleaned.split(sep)
        # Si el último grupo tiene 1-2 dígitos asumimos decimal y lo descartamos.
        # Si tiene 3+ dígitos, asumimos miles y eliminamos todos los separadores.
        if len(parts[-1]) <= 2:
            cleaned = parts[0]
        else:
            cleaned = "".join(parts)

    cleaned = re.sub(r"[^0-9-]", "", cleaned)
    if not cleaned:
        raise ValueError(f"No se pudo parsear la cantidad: {value!r}")
    return int(cleaned)


def should_run_tuesday_0800(now: datetime) -> bool:
    """Devuelve True solo si es martes exactamente a las 08:00."""
    return now.weekday() == 1 and now.hour == 8 and now.minute == 0


def evaluate_capital_evidence(
    evidence: dict[str, Any],
    expected_amount_eur: int = EXPECTED_CAPITAL_EUR,
) -> CapitalCheckResult:
    """Valida que la evidencia confirme la entrada de capital esperada."""
    confirmed = bool(evidence.get("confirmed", False))
    status = str(evidence.get("status", "")).strip().lower()
    amount_raw = evidence.get("amount_eur", "")

    if not confirmed:
        return CapitalCheckResult(False, "Evidencia no marcada como confirmada.")

    if status not in {"received", "confirmed", "settled"}:
        return CapitalCheckResult(False, f"Estado no válido para confirmar capital: {status!r}")

    try:
        amount = parse_eur_amount(amount_raw)
    except ValueError as exc:
        return CapitalCheckResult(False, f"Cantidad inválida en evidencia: {exc}")

    if amount != expected_amount_eur:
        return CapitalCheckResult(
            False,
            f"Cantidad inesperada: {amount} EUR (esperado: {expected_amount_eur} EUR).",
        )

    return CapitalCheckResult(True, f"Capital validado: {amount} EUR.")


def load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"JSON esperado tipo objeto en {path}, recibido: {type(data)!r}")
    return data


def send_telegram_success(
    message: str,
    post_func: Callable[..., Any] | None = None,
) -> None:
    """Envía una notificación de éxito usando el bot definido por entorno."""
    token = (os.getenv("TELEGRAM_BOT_TOKEN", "") or os.getenv("TELEGRAM_TOKEN", "")).strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        raise RuntimeError("Faltan TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN o TELEGRAM_CHAT_ID.")

    sender = post_func or requests.post
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": (
            f"{DEPLOY_BOT_USERNAME}\n\n"
            f"✅ {message}\n"
            f"🔱 Patente {PATENTE}\n"
            f"🏛️ {SOVEREIGN_PROTOCOL}"
        ),
        "parse_mode": "Markdown",
    }
    response = sender(api_url, json=payload, timeout=30)
    response.raise_for_status()


def run_supercommit_max(fast_mode: bool = True, script_path: Path | None = None) -> None:
    script = script_path or Path("supercommit_max.sh")
    if not script.exists():
        raise RuntimeError(f"No se encontró el script de despliegue: {script}")

    # Garantiza calidad básica de Bash antes de ejecutar.
    lint = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    if lint.returncode != 0:
        raise RuntimeError(
            "Validación Bash fallida para supercommit_max.sh.\n"
            f"STDERR:\n{lint.stderr}"
        )

    cmd = ["bash", str(script)]
    if fast_mode:
        cmd.append("--fast")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "supercommit_max.sh falló.\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def activate_dossier_fatality(log_path: Path, now: datetime, details: str) -> Path:
    """Registra activación documental de protección de capital (sin operaciones financieras)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dossier": "FATALITY",
        "mode": "GUARD_ONLY",
        "capital_protection": "ACTIVE",
        "activation_timestamp": now.isoformat(),
        "amount_expected_eur": EXPECTED_CAPITAL_EUR,
        "details": details,
        "legal_seal": f"{PATENTE} | {SOVEREIGN_PROTOCOL}",
    }
    with log_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return log_path


def build_memory_notes() -> str:
    return (
        "# bunker_sovereignty.ma\n\n"
        "## Memory Notes — TryOnYou\n\n"
        "- Archivo oficial de notas de memoria para automatizaciones soberanas.\n"
        "- Bot objetivo: @tryonyou_deploy_bot (token siempre por variable de entorno).\n"
        "- Sincronización técnica: ejecutar `supercommit_max.sh` en modo controlado.\n"
        "- Seguridad martes 08:00: validar evidencia documental de 450000 EUR.\n"
        "- Activación de Dossier Fatality: solo modo GUARD_ONLY (sin transacciones).\n"
        "- Estética/estabilidad: mantener Bash limpio y sin errores de ejecución.\n"
    )


def ensure_memory_file(path: Path) -> None:
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_memory_notes(), encoding="utf-8")


def _notify_or_warn(message: str, strict_notify: bool) -> None:
    try:
        send_telegram_success(message)
    except Exception as exc:  # pragma: no cover - solo para ejecución real
        warning = f"Notificación Telegram no enviada: {exc}"
        if strict_notify:
            raise RuntimeError(warning) from exc
        print(f"⚠️  {warning}")


def run_orchestration(args: argparse.Namespace, now: datetime | None = None) -> int:
    now = now or datetime.now()
    memory_path = Path(args.memory_file)
    evidence_path = Path(args.capital_evidence)

    ensure_memory_file(memory_path)
    _notify_or_warn(f"Memory Notes actualizada en {memory_path}.", args.strict_notify)

    if not args.skip_supercommit:
        run_supercommit_max(fast_mode=not args.full_supercommit)
        _notify_or_warn(
            "Supercommit_Max ejecutado: búnker Oberkampf 75011 sincronizado con galería web.",
            args.strict_notify,
        )

    do_security_check = args.force_security_check or should_run_tuesday_0800(now)
    if not do_security_check:
        print("ℹ️  Verificación de seguridad programada para martes 08:00 (no ejecutada ahora).")
        return 0

    if not evidence_path.exists():
        print(f"⚠️  Evidencia no encontrada en {evidence_path}.")
        return 2

    evidence = load_json_file(evidence_path)
    result = evaluate_capital_evidence(evidence)
    if not result.ok:
        print(f"⚠️  Verificación de capital bloqueada: {result.message}")
        return 3

    log_path = activate_dossier_fatality(
        log_path=DOSSIER_LOG_FILE,
        now=now,
        details=(
            f"{result.message} Confirmación documental procesada para ventana martes 08:00."
        ),
    )
    _notify_or_warn(
        f"Dossier Fatality activado en modo GUARD_ONLY. Registro: {log_path}.",
        args.strict_notify,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Orquestador seguro de autonomía total TryOnYou.",
    )
    parser.add_argument(
        "--memory-file",
        default=DEFAULT_MEMORY_FILE,
        help=f"Ruta de Memory Notes (default: {DEFAULT_MEMORY_FILE}).",
    )
    parser.add_argument(
        "--capital-evidence",
        default=DEFAULT_EVIDENCE_FILE,
        help=f"Ruta JSON con evidencia de capital (default: {DEFAULT_EVIDENCE_FILE}).",
    )
    parser.add_argument(
        "--skip-supercommit",
        action="store_true",
        help="Omite la ejecución de supercommit_max.sh.",
    )
    parser.add_argument(
        "--full-supercommit",
        action="store_true",
        help="Ejecuta supercommit_max.sh completo (sin --fast).",
    )
    parser.add_argument(
        "--force-security-check",
        action="store_true",
        help="Ejecuta la verificación de seguridad aunque no sea martes 08:00.",
    )
    parser.add_argument(
        "--strict-notify",
        action="store_true",
        help="Falla si no se puede notificar por Telegram.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_orchestration(args)
    except Exception as exc:
        print(f"❌ Error en orquestación: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
