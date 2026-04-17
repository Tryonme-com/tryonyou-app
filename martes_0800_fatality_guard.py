"""
Guardia soberana: martes 08:00, validar entrada 450.000 EUR y activar Dossier Fatality.

Uso:
  python3 martes_0800_fatality_guard.py

Variables de entorno:
  CAPITAL_ENTRY_EUR=450000
  TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN / TRYONYOU_DEPLOY_BOT_TOKEN
  TELEGRAM_CHAT_ID / TRYONYOU_DEPLOY_BOT_CHAT_ID

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Tuple


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
STATE_FILE = LOG_DIR / "dossier_fatality_state.json"
TARGET_AMOUNT = 450000.0
TARGET_WEEKDAY = 1  # Tuesday (Monday=0)
TARGET_HOUR = 8


@dataclass
class GuardResult:
    status: str
    reason: str
    amount: float
    now_iso: str


def _env_token() -> str:
    return (
        os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
    )


def _env_chat_id() -> str:
    return (
        os.getenv("TRYONYOU_DEPLOY_BOT_CHAT_ID", "").strip()
        or os.getenv("TELEGRAM_CHAT_ID", "").strip()
    )


def _parse_amount() -> float:
    raw = os.getenv("CAPITAL_ENTRY_EUR", "").strip()
    if not raw:
        return 0.0
    normalized = raw.replace(" ", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized:
        if normalized.count(",") == 1 and len(normalized.split(",")[1]) <= 2:
            normalized = normalized.replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "." in normalized:
        if not (normalized.count(".") == 1 and len(normalized.split(".")[1]) <= 2):
            normalized = normalized.replace(".", "")
    try:
        return float(normalized)
    except ValueError:
        return 0.0


def _is_target_window(now: datetime) -> bool:
    if os.getenv("FATALITY_GUARD_FORCE_WINDOW", "").strip() in {"1", "true", "yes"}:
        return True
    return now.weekday() == TARGET_WEEKDAY and now.hour == TARGET_HOUR


def _run_fatality_dossier() -> Tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "fatality_investors.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "").strip()
    if proc.stderr:
        output = f"{output}\n{proc.stderr.strip()}".strip()
    return proc.returncode, output


def _write_state(result: GuardResult, fatality_code: int, fatality_output: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": result.status,
        "reason": result.reason,
        "amount_eur": result.amount,
        "timestamp": result.now_iso,
        "fatality_exit_code": fatality_code,
        "fatality_output": fatality_output[:2000],
    }
    STATE_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _notify(message: str) -> bool:
    token = _env_token()
    chat_id = _env_chat_id()
    if not token or not chat_id:
        return False
    try:
        import requests
    except Exception:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(
            url,
            json={"chat_id": chat_id, "text": message},
            timeout=30,
        )
        return res.status_code == 200
    except Exception:
        return False


def evaluate() -> GuardResult:
    now = datetime.now()
    amount = _parse_amount()
    if not _is_target_window(now):
        return GuardResult(
            status="WINDOW_MISMATCH",
            reason="Fuera de martes 08:00, no se activa el protocolo.",
            amount=amount,
            now_iso=now.isoformat(),
        )
    if amount < TARGET_AMOUNT:
        return GuardResult(
            status="CAPITAL_PENDING",
            reason="Capital inferior al umbral de 450.000 EUR.",
            amount=amount,
            now_iso=now.isoformat(),
        )
    return GuardResult(
        status="CAPITAL_CONFIRMED",
        reason="Entrada de 450.000 EUR confirmada en ventana objetivo.",
        amount=amount,
        now_iso=now.isoformat(),
    )


def main() -> int:
    result = evaluate()
    if result.status != "CAPITAL_CONFIRMED":
        _write_state(result, 0, "Dossier Fatality no ejecutado.")
        _notify(
            "⚠️ Guardia Martes 08:00: "
            f"{result.status} | {result.reason} | amount={result.amount:.2f} EUR"
        )
        print(f"{result.status}: {result.reason}")
        return 0

    code, output = _run_fatality_dossier()
    _write_state(result, code, output)
    if code == 0:
        _notify(
            "✅ Guardia Martes 08:00: 450.000 EUR confirmado y Dossier Fatality activado."
        )
        print("CAPITAL_CONFIRMED: Dossier Fatality activado.")
        return 0

    _notify(
        "❌ Guardia Martes 08:00: capital confirmado, pero Dossier Fatality falló. "
        f"exit_code={code}"
    )
    print("ERROR: Dossier Fatality devolvió error.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
