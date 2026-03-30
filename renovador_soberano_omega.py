"""Renovador soberano Omega: Oráculo (Gemini) + Make/Jules + Telegram opcional.

Uso:
  export GOOGLE_STUDIO_API_KEY='clave_nueva_desde_aistudio.google.com'
  python3 renovador_soberano_omega.py

El oráculo hereda ORACLE_SKIP_GIT y ORACLE_GIT_PUSH_FORCE como en oraculo_studio.py.

Opcional:
  MAKE_WEBHOOK_URL — ping a Jules/Make tras consulta exitosa
  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID — aviso final
  RENOVADOR_SKIP_MAKE=1 | RENOVADOR_SKIP_TELEGRAM=1

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PATENT = "PCT/EP2025/067317"
STAMP = "@CertezaAbsoluta @lo+erestu"


def _api_key() -> str:
    return (
        os.environ.get("GOOGLE_STUDIO_API_KEY", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
    )


def _run_oracle(env: dict[str, str]) -> int:
    print("--- [1/3] Oráculo Studio (Gemini) → decision_estudio.json ---")
    r = subprocess.run(
        [sys.executable, str(ROOT / "oraculo_studio.py")],
        cwd=ROOT,
        env=env,
        text=True,
    )
    return r.returncode


def _make_jules_ping() -> bool:
    if os.environ.get("RENOVADOR_SKIP_MAKE", "").strip() == "1":
        print("--- [2/3] Make/Jules — omitido (RENOVADOR_SKIP_MAKE=1) ---")
        return True

    webhook = os.environ.get("MAKE_WEBHOOK_URL", "").strip()
    if not webhook:
        print("--- [2/3] Make/Jules — sin MAKE_WEBHOOK_URL (opcional) ---")
        return True

    print("--- [2/3] Make/Jules — sincronizando escenario ---")
    from shopify_make_bridge import ShopifyMakeBridge

    bridge = ShopifyMakeBridge()
    datos = {
        "nombre": "Renovación clave Google Studio + Oráculo",
        "rcs": "omega-oracle-v10",
        "pieza": "decision_estudio.json",
        "evento": "GOOGLE_STUDIO_KEY_SYNC",
    }
    return bridge.sync_colaborador(datos)


def _telegram_notify(oracle_ok: bool, make_ok: bool) -> None:
    if os.environ.get("RENOVADOR_SKIP_TELEGRAM", "").strip() == "1":
        print("--- [3/3] Telegram — omitido (RENOVADOR_SKIP_TELEGRAM=1) ---")
        return

    print("--- [3/3] Telegram — aviso de cierre ---")
    try:
        from telegram_signal_system import TryOnYouSignals

        sig = TryOnYouSignals()
    except RuntimeError:
        print("Sin TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID — aviso omitido.")
        return
    except ImportError as e:
        print(f"módulo Telegram no disponible: {e}", file=sys.stderr)
        return

    parts = [
        "*Renovador soberano Omega*",
        f"Oráculo: {'OK' if oracle_ok else 'FALLO'}",
        f"Make/Jules: {'OK' if make_ok else 'revisa webhook'}",
        f"PATENTE: {PATENT}",
        STAMP,
    ]
    sig.send_sovereignty_signal("\n".join(parts))


def main() -> int:
    key = _api_key()
    if not key:
        print(
            "Exporta GOOGLE_STUDIO_API_KEY (o GEMINI_API_KEY) con la clave nueva de "
            "https://aistudio.google.com/",
            file=sys.stderr,
        )
        return 1

    env = os.environ.copy()
    env["GOOGLE_STUDIO_API_KEY"] = key

    code = _run_oracle(env)
    if code != 0:
        _telegram_notify(oracle_ok=False, make_ok=False)
        print(f"Oráculo terminó con código {code}.", file=sys.stderr)
        return code

    make_ok = _make_jules_ping()
    _telegram_notify(oracle_ok=True, make_ok=make_ok)

    if not make_ok:
        print("Make devolvió error; revisa MAKE_WEBHOOK_URL y el escenario eu2.", file=sys.stderr)
        return 1

    print("\nRenovación soberana completada (oráculo + sincronización).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
