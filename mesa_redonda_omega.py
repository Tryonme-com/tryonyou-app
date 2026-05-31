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
# Frase obligatoria en commits (regla Agente @Pau / Stirpe Lafayette).
PROTOCOL_PHRASE = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"


class MesaRedondaOmega:
    def __init__(self) -> None:
        self.bunker_id = "STIRPE-LAFAYETTE-V10"
        self.integrantes = ["LISTOS", "GEMINI", "COPILOT", "MANUS", "AGENTE70", "JULES"]
        self.patent = PATENT

    def tomar_decision_autonoma(self) -> dict:
        print(f"--- MESA REDONDA ACTIVA: {self.bunker_id} ---")

        # 1. JULES & LISTOS: decisión de stock
        decision_comercial = "ACTIVAR CIERRE POR ESCASEZ: Solo 2 unidades SAC Museum."
        # 2. AGENTE70 & GEMINI: decisión de voz (V10: stability 0.85)
        decision_voz = "Lily (Gemela Perfecta) valida el fit con Stability 0.85."
        # 3. MANUS & COPILOT: decisión técnica
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
            "sesion": {
                "lily": "Niña Perfecta (Lily) — sello de sesión V10, voz EXAVITQu4vr4xnNLTejx",
                "jules_loi": (
                    "Verificación LOI Guy Moquet (París 17): commerce, showroom, pop-up, "
                    "axe Saint-Ouen — cruce con assets/real_estate/"
                ),
            },
            "status": "BAJO PROTOCOLO DE SOBERANÍA V10 - FOUNDER: RUBÉN",
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
        print(f"Decisiones comunicadas (señal push): {acta['decisiones']}")

        if os.environ.get("MESA_SKIP_GIT", "").strip().lower() in ("1", "true", "yes", "on"):
            print("MESA_SKIP_GIT: omitiendo git add/commit/push.")
            return

        msg = (
            "MESA REDONDA: decisiones Listos, Gemini, Copilot, Manus, AGENTE70, Jules. "
            f"{PROTOCOL_PHRASE}. {STAMP_C} {STAMP_L} {PATENT}"
        )
        for stamp in (STAMP_C, STAMP_L, PATENT):
            if stamp not in msg:
                print(f"Error interno: falta sello en mensaje: {stamp}", file=sys.stderr)
                sys.exit(1)
        if PROTOCOL_PHRASE not in msg:
            print("Error interno: falta frase de protocolo en mensaje.", file=sys.stderr)
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

        force_push = os.environ.get("MESA_GIT_PUSH_FORCE", "").strip() == "1"
        upstream = self._git("rev-parse", "--verify", "@{u}", check=False)
        has_upstream = upstream.returncode == 0

        if not force_push and not has_upstream:
            if did_commit:
                print(
                    "Commit creado en local. Sin push: no hay upstream (@{u}). "
                    "Configura tracking (p. ej. git push -u origin <rama>) o empuja a mano.",
                )
            else:
                print("Sin push: no hay upstream (@{u}). Configura tracking o empuja a mano.")
            return

        if not force_push:
            if not did_commit:
                ahead_cp = self._git("rev-list", "--count", "@{u}..HEAD", check=False)
                try:
                    ahead = int((ahead_cp.stdout or "0").strip() or "0")
                except ValueError:
                    ahead = 0
                if ahead <= 0:
                    print(
                        "Sin push: indice sin cambios nuevos y la rama no va por delante del remoto.",
                    )
                    return

        if force_push:
            br = self._git("rev-parse", "--abbrev-ref", "HEAD")
            branch = (br.stdout or "").strip()
            if not branch or branch == "HEAD":
                print(
                    "Sin push forzado: HEAD detached o rama sin nombre. "
                    "Cambia a una rama con nombre o empuja a mano.",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(
                f"ADVERTENCIA: MESA_GIT_PUSH_FORCE=1 -> "
                f"git push --force-with-lease origin {branch}",
            )
            self._git("push", "--force-with-lease", "origin", branch)
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
