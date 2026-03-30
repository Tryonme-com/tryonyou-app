"""Oráculo Mesa de los Listos — Gemini vía Google AI Studio. Sella ``decision_estudio.json``; git opcional.

Requiere: pip install google-generativeai

Entorno: GOOGLE_STUDIO_API_KEY (o GEMINI_API_KEY). Sin push forzado por defecto.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "decision_estudio.json"

PATENT = "PCT/EP2025/067317"
STAMP_C = "@CertezaAbsoluta"
STAMP_L = "@lo+erestu"
PROTOCOL_PHRASE = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"


def _api_key() -> str:
    return (
        os.environ.get("GOOGLE_STUDIO_API_KEY", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
    )


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", t, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


class OraculoStudio:
    def __init__(self) -> None:
        key = _api_key()
        if not key:
            raise RuntimeError(
                "Define GOOGLE_STUDIO_API_KEY o GEMINI_API_KEY en el entorno."
            )
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise RuntimeError(
                "pip install google-generativeai — " + str(e)
            ) from e

        genai.configure(api_key=key)
        model_name = os.environ.get("ORACLE_GEMINI_MODEL", "gemini-1.5-flash").strip()
        self._genai = genai
        self.model = genai.GenerativeModel(model_name)
        self.patent = PATENT
        self.founder = "Rubén Espinar Rodríguez"

    def consultar_mesa_redonda(self) -> dict:
        """Gemini como Oráculo de los Listos; respuesta estructurada en JSON."""
        prompt = f"""
Actúa como el Oráculo de la Mesa de los Listos para el proyecto TryOnYou.
Contexto: Fundador {self.founder}, Patente {self.patent}.
Tarea: Analiza el inventario VIP (conceptual Shopify) y propone nivel de escasez y una acción.
Regla: Si el fit conceptual es >99%, recomienda "baño de oro líquido".
Responde SOLO un objeto JSON válido, sin markdown, con claves:
inventory_assessment, scarcity_level, fit_threshold_note, recommended_action, rationale (breve).
""".strip()

        print("[GOOGLE STUDIO / Gemini] Consultando Mesa Redonda...")
        response = self.model.generate_content(prompt)
        raw = (response.text or "").strip()

        payload: dict = {
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "founder": self.founder,
            "patente": self.patent,
            "model": os.environ.get("ORACLE_GEMINI_MODEL", "gemini-1.5-flash"),
            "raw_response": raw,
        }

        cleaned = _strip_code_fence(raw)
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                payload["decision"] = parsed
        except json.JSONDecodeError:
            payload["decision"] = None
            payload["parse_error"] = "La respuesta no era JSON estricto; ver raw_response."

        DECISION_PATH.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Sello: {DECISION_PATH.resolve()}")
        return payload

    def conectar_a_cursor(self) -> int:
        """git add/commit/push de decision_estudio.json con sellos TryOnYou (sin force por defecto)."""
        if os.environ.get("ORACLE_SKIP_GIT", "").strip() == "1":
            print("ORACLE_SKIP_GIT=1 — sin git.")
            return 0

        msg = (
            f"AGENCY: Google AI Studio — Mesa de los Listos. {PROTOCOL_PHRASE}. "
            f"{STAMP_C} {STAMP_L} {PATENT}"
        )
        for s in (STAMP_C, STAMP_L, PATENT, PROTOCOL_PHRASE):
            if s not in msg:
                print(f"Falta sello en mensaje: {s}", file=sys.stderr)
                return 1

        _git("add", "-f", str(DECISION_PATH.name))
        st = _git("diff", "--cached", "--quiet", check=False)
        if st.returncode == 0:
            print("Sin cambios en índice (decision_estudio.json igual).")
            return 0

        _git("commit", "-m", msg)
        print("Commit creado.")

        if os.environ.get("ORACLE_GIT_PUSH_FORCE", "").strip() == "1":
            br = _git("rev-parse", "--abbrev-ref", "HEAD")
            branch = (br.stdout or "").strip()
            if not branch or branch == "HEAD":
                print("Sin push: HEAD detached.", file=sys.stderr)
                return 1
            _git("push", "--force-with-lease", "origin", branch)
        else:
            _git("push")

        print("Push completado.")
        return 0


def main() -> int:
    try:
        o = OraculoStudio()
        o.consultar_mesa_redonda()
        return o.conectar_a_cursor()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print((e.stderr or e.stdout or "")[:2000], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
