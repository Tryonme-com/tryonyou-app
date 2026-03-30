"""Mesa redonda Omega STIRPE-LAFAYETTE-V10: acta JSON + git opcional (sellos TryOnYou en commit)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ACTA_PATH = REPO_ROOT / "acta_mesa_redonda.json"

# Sellos obligatorios en mensajes de commit (TryOnYou).
STAMP_C = "@CertezaAbsoluta"
STAMP_L = "@lo+erestu"
PATENT = "PCT/EP2025/067317"


class MesaRedondaOmega:
    def __init__(self) -> None:
        self.bunker_id = "STIRPE-LAFAYETTE-V10"
        self.integrantes = ["LISTOS", "GEMINI", "COPILOT", "MANUS", "AGENTE70", "JULES"]
        self.patent = PATENT

    def tomar_decision_autonoma(self) -> dict:
        print(f"--- MESA REDONDA ACTIVA: {self.bunker_id} ---")

        decision_comercial = "ACTIVAR CIERRE POR ESCASEZ: Solo 2 unidades SAC Museum."
        decision_voz = "Lily (Gemela Perfecta) valida el fit con Stability 0.85."
        decision_tecnica = "Inyectar Biometric Matcher V10 en tryonyou.app."

        acta = {
            "timestamp": datetime.now().isoformat(),
            "bunker_id": self.bunker_id,
            "integrantes": self.integrantes,
            "patent": self.patent,
            "decisiones": {
                "comercial": decision_comercial,
                "voz": decision_voz,
                "tecnica": decision_tecnica,
            },
            "status": "BAJO PROTOCOLO DE SOBERANIA V10 - FOUNDER: RUBEN",
        }

        ACTA_PATH.write_text(json.dumps(acta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return acta

    def _git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def comunicar_a_gemini(self, acta: dict) -> None:
        print(f"Decisiones comunicadas: {acta['decisiones']}")

        if os.environ.get("MESA_SKIP_GIT", "").strip().lower() in ("1", "true", "yes", "on"):
            print("MESA_SKIP_GIT: omitiendo git add/commit/push.")
            return

        msg = (
            "MESA REDONDA Omega: acta consolidada (comercial/voz/tecnica). "
            f"{STAMP_C} {STAMP_L} {PATENT}"
        )
        for stamp in (STAMP_C, STAMP_L, PATENT):
            if stamp not in msg:
                print(f"Error interno: falta sello en mensaje: {stamp}", file=sys.stderr)
                sys.exit(1)

        self._git("add", "-A")
        st = self._git("diff", "--cached", "--quiet", check=False)
        if st.returncode == 0:
            print("Nada nuevo en el indice tras git add (sin commit en esta pasada).")
            did_commit = False
        else:
            self._git("commit", "-m", msg)
            print("Commit creado.")
            did_commit = True

        upstream = self._git("rev-parse", "--verify", "@{u}", check=False)
        if not did_commit:
            if upstream.returncode != 0:
                print("Sin push: no hay upstream (@{u}). Configura tracking o empuja a mano.")
                return
            ahead_cp = self._git("rev-list", "--count", "@{u}..HEAD", check=False)
            try:
                ahead = int((ahead_cp.stdout or "0").strip() or "0")
            except ValueError:
                ahead = 0
            if ahead <= 0:
                print("Sin push: indice sin cambios nuevos y la rama no va por delante del remoto.")
                return

        if os.environ.get("MESA_GIT_PUSH_FORCE", "").strip() == "1":
            print("ADVERTENCIA: MESA_GIT_PUSH_FORCE=1 -> git push --force-with-lease origin main")
            self._git("push", "--force-with-lease", "origin", "main")
        else:
            self._git("push")
        print("Push completado (rama actual / upstream por defecto).")


def main() -> int:
    mesa = MesaRedondaOmega()
    acta = mesa.tomar_decision_autonoma()
    mesa.comunicar_a_gemini(acta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
