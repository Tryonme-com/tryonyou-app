"""
Autonomía total TryOnYou:
- Ejecuta SUPERCOMMIT_MAX (búnker Oberkampf 75011 ↔ galería web).
- Notifica éxitos con @tryonyou_deploy_bot usando token/chat desde entorno.
- Programa/activa Dossier Fatality para martes 08:00 con validación explícita.

Seguridad:
- Nunca confirma ingresos reales de forma automática sin evidencia explícita.
- No hardcodea secretos en código.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parent
DOSSIER_FILE: Final[Path] = ROOT / "dossier_fatality.json"
STATE_FILE: Final[Path] = ROOT / "dossier_fatality_state.json"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _notify(text: str) -> None:
    """
    Envía señal al bot @tryonyou_deploy_bot (Telegram API) con credenciales por entorno.
    Variables:
      - TRYONYOU_DEPLOY_BOT_TOKEN (preferida) o TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN
      - TRYONYOU_DEPLOY_CHAT_ID (preferida) o TELEGRAM_CHAT_ID
    """
    token = _env("TRYONYOU_DEPLOY_BOT_TOKEN") or _env("TELEGRAM_BOT_TOKEN") or _env("TELEGRAM_TOKEN")
    chat = _env("TRYONYOU_DEPLOY_CHAT_ID") or _env("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("ℹ️ Notificación omitida: faltan token/chat_id de @tryonyou_deploy_bot.")
        return

    payload = urllib.parse.urlencode(
        {
            "chat_id": chat,
            "text": f"@tryonyou_deploy_bot ✅ {text}\nPatente: PCT/EP2025/067317",
        }
    ).encode("utf-8")
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status}")
        print("📡 Notificación enviada al bot de despliegue.")
    except Exception as exc:
        print(f"⚠️ No se pudo notificar al bot: {exc}")


def _run(cmd: list[str], cwd: Path = ROOT) -> int:
    print(">", " ".join(cmd))
    return subprocess.run(cmd, cwd=str(cwd), check=False).returncode


def _run_supercommit() -> int:
    script = ROOT / "supercommit_max.sh"
    if not script.is_file():
        print("❌ supercommit_max.sh no existe.")
        return 2
    rc = _run(["bash", str(script)])
    if rc == 0:
        _notify("Supercommit_Max ejecutado: búnker Oberkampf 75011 sincronizado con la galería web.")
    return rc


def _load_json(path: Path, fallback: dict) -> dict:
    if not path.is_file():
        return dict(fallback)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(fallback)


def _save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _next_tuesday_0800(now: dt.datetime) -> dt.datetime:
    # Lunes=0 ... Domingo=6 ; martes=1
    days_ahead = (1 - now.weekday()) % 7
    target = now + dt.timedelta(days=days_ahead)
    target = target.replace(hour=8, minute=0, second=0, microsecond=0)
    if target <= now:
        target += dt.timedelta(days=7)
    return target


def _should_activate(now: dt.datetime) -> tuple[bool, str]:
    """
    Permite activación solo si:
    - Es martes a partir de las 08:00 local
    - y la validación de ingreso está marcada explícitamente en entorno.
    """
    if now.weekday() != 1:
        return False, "No es martes."
    if now.hour < 8:
        return False, "Aún no son las 08:00."
    confirmed = _env("TRYONYOU_CAPITAL_450K_CONFIRMED").lower() in {"1", "true", "yes", "on"}
    if not confirmed:
        return False, "Falta confirmación explícita TRYONYOU_CAPITAL_450K_CONFIRMED=1."
    return True, "Ventana válida."


def _activate_dossier_fatality(now: dt.datetime) -> int:
    dossier = _load_json(DOSSIER_FILE, fallback={"estrategia": "DOSSIER FATALITY V10"})
    state = _load_json(
        STATE_FILE,
        fallback={
            "capital_expected_eur": 450000,
            "capital_confirmed": False,
            "scheduled_for": "",
            "activated_at": "",
            "status": "PENDING_VALIDATION",
        },
    )

    can_activate, reason = _should_activate(now)
    next_slot = _next_tuesday_0800(now).isoformat()
    state["scheduled_for"] = next_slot

    if not can_activate:
        state["status"] = "PENDING_VALIDATION"
        state["capital_confirmed"] = False
        _save_json(STATE_FILE, state)
        print(f"ℹ️ Dossier Fatality en espera: {reason} Próxima ventana: {next_slot}")
        _notify(f"Dossier Fatality en espera: {reason} Próxima ventana {next_slot}.")
        return 0

    state["status"] = "ACTIVE"
    state["capital_confirmed"] = True
    state["activated_at"] = now.isoformat()
    dossier["capital_guard"] = {
        "target_amount_eur": 450000,
        "confirmed": True,
        "activated_at": now.isoformat(),
        "protocol": "DOSSIER_FATALITY_V10",
    }

    _save_json(DOSSIER_FILE, dossier)
    _save_json(STATE_FILE, state)
    _notify("Entrada 450.000€ confirmada y Dossier Fatality ACTIVADO para protección de capital.")
    print("✅ Dossier Fatality activado.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomía total TryOnYou (supercommit + seguridad).")
    parser.add_argument(
        "--only",
        choices=["all", "supercommit", "fatality"],
        default="all",
        help="Selecciona qué bloque ejecutar.",
    )
    args = parser.parse_args()

    now = dt.datetime.now()
    rc = 0

    if args.only in {"all", "supercommit"}:
        rc = _run_supercommit()
        if rc != 0:
            return rc

    if args.only in {"all", "fatality"}:
        rc = _activate_dossier_fatality(now)
        if rc != 0:
            return rc

    print("✅ Autonomía total completada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
