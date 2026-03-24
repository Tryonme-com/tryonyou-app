"""
Unificar V10 — limpieza de puerto 5173, comprobación opcional Gemini, arranque Vite (mirror_ui).

Clave Gemini / AI Studio solo por entorno (nunca en el código):
  GEMINI_API_KEY, GOOGLE_API_KEY o VITE_GOOGLE_API_KEY

  pip install google-generativeai
  cd mirror_ui && npm install
  python3 unificar_v10.py

Opcional: E50_PROJECT_ROOT (raíz del repo; por defecto carpeta del script).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path

PATENT = "PCT/EP2025/067317"
SIREN = "94361019600017"
VITE_PORT = 5173
VITE_URL = f"http://127.0.0.1:{VITE_PORT}"


def _root() -> Path:
    return Path(os.environ.get("E50_PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()


def _mirror_ui(root: Path) -> Path:
    return root / "mirror_ui"


def _gemini_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
        or os.environ.get("VITE_GOOGLE_API_KEY", "").strip()
    )


def _free_port_5173() -> None:
    print(f"🧹 Liberando puerto {VITE_PORT} si está ocupado...")
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        subprocess.run(
            f"lsof -ti:{VITE_PORT} | xargs kill -9 2>/dev/null || true",
            shell=True,
            stderr=subprocess.DEVNULL,
        )
    elif os.name == "nt":
        ps = (
            "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue "
            "| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            stderr=subprocess.DEVNULL,
        )
    print("✅ Listo (o el puerto ya estaba libre).")


def _pau_gemini_probe() -> None:
    key = _gemini_key()
    if not key:
        print("ℹ️  Sin GEMINI_API_KEY / GOOGLE_API_KEY / VITE_GOOGLE_API_KEY: se omite la prueba PAU.")
        return
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            "gemini-1.5-pro",
            generation_config={"temperature": 0.1, "max_output_tokens": 512},
        )
        r = model.generate_content(
            "V10 status: responde en una frase si el espejo digital está listo para retail (LVT-FRA)."
        )
        text = (r.text or "").strip().replace("\n", " ")
        print(f"✨ PAU (Gemini): {text[:200]}{'…' if len(text) > 200 else ''}")
    except ImportError:
        print("⚠️  Instala: pip install google-generativeai")
    except Exception as e:
        print(f"⚠️  Conexión IA: {e}")


def ejecutar_secuencia_maestra() -> int:
    root = _root()
    ui = _mirror_ui(root)
    print(f"\n⚡ [{datetime.now().strftime('%H:%M:%S')}] PROTOCOLO AUTÓNOMO V10")
    print("-" * 50)

    if not (ui / "package.json").is_file():
        print(f"❌ No hay mirror_ui/package.json bajo {root}")
        return 1

    _free_port_5173()
    print("🧠 Sincronización opcional con Gemini (AI Studio)...")
    _pau_gemini_probe()
    print(f"⚖️  Patente {PATENT} · SIREN {SIREN} · TRYONYOU (referencia operativa).")

    print(f"\n🚀 Arrancando Vite en {ui} …")
    try:
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(ui),
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("❌ No se encontró npm. Instala Node y ejecuta: cd mirror_ui && npm install")
        return 1

    time.sleep(2.5)
    print(f"🌐 Abriendo {VITE_URL} …")
    webbrowser.open(VITE_URL)
    print("⌛ Vite en marcha. Ctrl+C en esta terminal para detener.\n")
    try:
        return 0 if proc.wait() == 0 else proc.returncode or 1
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("\n🛑 Detenido.")
        return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar_secuencia_maestra())
