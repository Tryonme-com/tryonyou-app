"""
Consolidación Omega — notificación Make + limpieza opcional de archivos + Git opcional.

NUNCA pegues el webhook de Make en el código. Usa MAKE_WEBHOOK_URL en el entorno.

Git automático (CONSOLIDACION_GIT=1): el mensaje debe cumplir las reglas del equipo
(@CertezaAbsoluta, @lo+erestu, PCT/EP2025/067317); si no, usa supercommit_max.sh a mano.

  export MAKE_WEBHOOK_URL='https://hook.eu2.make.com/...'
  python3 consolidacion_total_omega.py

  CONSOLIDACION_GIT=1 python3 consolidacion_total_omega.py   # solo si quieres add+commit

Opcional Make:
  CONSOLIDACION_MAKE_ACTION=omega_auto_run
  CONSOLIDACION_MAKE_AGENTS=50          # número entero en el JSON hacia Make

No implementa git push: hazlo tú tras revisar el diff (evita empujar a main a ciegas).

Patente (ref.): PCT/EP2025/067317
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime

DEUDA_REF = os.environ.get(
    "CONSOLIDACION_DEUDA_TEXTO",
    "16.200 € TTC (referencia interna — verificar en contabilidad)",
).strip()

DEFAULT_BASURA = [
    "terminal_cleanup.py",
    "check_system_health.py",
    "deploy_omega_final.py",
]

# Nunca borrar por script (núcleo bunker / API / orquestación).
_FORBIDDEN_DELETE: frozenset[str] = frozenset(
    {
        "omega_auto_pilot.py",
        "consolidacion_total_omega.py",
        "bunker_full_orchestrator.py",
        "composite_bunker_executor.py",
        "vetos_core_inference.py",
        "api/index.py",
        "supercommit_max.sh",
        "vercel.json",
    }
)


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _cleanup_orphans() -> list[str]:
    raw = os.environ.get("CONSOLIDACION_CLEANUP_FILES", "").strip()
    names = [x.strip() for x in raw.split(",") if x.strip()] if raw else DEFAULT_BASURA
    removed: list[str] = []
    for archivo in names:
        base = os.path.basename(archivo)
        if base in _FORBIDDEN_DELETE:
            print(
                f"⛔ Omitido (protegido, no se borra): {archivo}",
                file=sys.stderr,
            )
            continue
        if os.path.isfile(archivo):
            try:
                os.remove(archivo)
                removed.append(archivo)
                print(f"🔥 Eliminado: {archivo}")
            except OSError as e:
                print(f"⚠️  No se pudo eliminar {archivo}: {e}", file=sys.stderr)
    return removed


def _post_make() -> int:
    url = (os.environ.get("MAKE_WEBHOOK_URL") or "").strip()
    if not url:
        print(
            "ℹ️  MAKE_WEBHOOK_URL no definido: se omite POST a Make.",
            file=sys.stderr,
        )
        return 0
    payload: dict = {
        "status": "consolidated_run",
        "action": (os.environ.get("CONSOLIDACION_MAKE_ACTION") or "").strip()
        or "consolidated_run",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "deuda_ref": DEUDA_REF,
    }
    agents_raw = os.environ.get("CONSOLIDACION_MAKE_AGENTS", "").strip()
    if agents_raw.isdigit():
        payload["agents"] = int(agents_raw)
    try:
        import requests

        r = requests.post(url, json=payload, timeout=120)
        print(f"📡 Make.com: HTTP {r.status_code}")
        return 0 if r.status_code < 500 else 1
    except Exception as e:
        print(f"⚠️  Error Make: {e}", file=sys.stderr)
        return 1


def _git_optional() -> None:
    if not _truthy("CONSOLIDACION_GIT"):
        print("ℹ️  CONSOLIDACION_GIT no activado: sin git add/commit.")
        print("   Para sellar: ./supercommit_max.sh 'mensaje @CertezaAbsoluta @lo+erestu PCT/EP2025/067317'")
        return
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=os.getcwd())
        msg = (
            f"Bloqueo nodo referencia — consolidación Omega. Deuda (ref.): {DEUDA_REF} "
            "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
        )
        subprocess.run(["git", "commit", "-m", msg], check=True, cwd=os.getcwd())
        print(f"✅ Git commit: {msg[:80]}…")
    except subprocess.CalledProcessError:
        print("ℹ️  Git: sin cambios nuevos o commit no aplicable.")


def consolidacion_total() -> int:
    print("🚀 Ciclo de consolidación Omega (referencia 75001)")
    _cleanup_orphans()
    code = _post_make()
    _git_optional()
    print(
        f"\n🔱 Autonomía de script [{datetime.now().strftime('%H:%M')}]. "
        "Revisa Make y contabilidad antes de acciones reales."
    )
    return code


if __name__ == "__main__":
    raise SystemExit(consolidacion_total())
