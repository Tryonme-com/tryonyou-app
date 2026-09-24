"""
Arranque búnker soberanía V10: puerto 5173, Gemini (opcional), aviso Telegram (opcional), Vite en la raíz.

Secretos solo por entorno (nunca en el código):
  GEMINI_API_KEY / GOOGLE_API_KEY / VITE_GOOGLE_API_KEY
  TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) + TELEGRAM_CHAT_ID

Opcional:
  TELEGRAM_FORMAT=markdown     — mensaje PAU con parse_mode Markdown (clásico)
  SKIP_TELEGRAM=1              — no envía mensaje
  BUNKER_MONTO_BRUTO_EUR       — texto mostrado (default del ejemplo)
  BUNKER_GASTOS_EUR
  BUNKER_NETO_EUR
  BUNKER_HITO_FECHA            — ej. "9 de mayo"

  pip install requests google-generativeai
  python3 arranque_bunker_soberania.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import webbrowser
from datetime import datetime

import requests

from unificar_v10 import (
    PATENT,
    SIREN,
    VITE_PORT,
    VITE_URL,
    _free_port_5173,
    _gemini_key,
    _mirror_ui,
    _root,
)


def _telegram_credentials() -> tuple[str, str]:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    return token, chat


def enviar_telegram(mensaje: str) -> bool:
    token, chat = _telegram_credentials()
    if not token or not chat:
        print(
            "ℹ️  Sin TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) / TELEGRAM_CHAT_ID: se omite "
            "Telegram."
        )
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    fmt = os.environ.get("TELEGRAM_FORMAT", "plain").strip().lower()
    payload: dict = {"chat_id": chat, "text": mensaje}
    if fmt == "markdown":
        payload["parse_mode"] = "Markdown"
    try:
        r = requests.post(
            url,
            json=payload,
            timeout=30,
        )
        if r.status_code == 200:
            print("✅ Mensaje enviado a Telegram.")
            return True
        print(f"❌ Telegram HTTP {r.status_code}: {r.text[:200]}")
    except requests.RequestException as e:
        print(f"❌ Fallo de red Telegram: {e}")
    return False


def _pau_robert_mayo() -> None:
    key = _gemini_key()
    if not key:
        print("ℹ️  Sin clave Gemini: se omite sincronización PAU.")
        return
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        r = model.generate_content(
            "Confirma en una frase el estado del Robert Engine TryOnYou V10 para el 9 de mayo."
        )
        text = (r.text or "").strip().replace("\n", " ")
        print(f"✨ IA Studio: {text[:120]}{'…' if len(text) > 120 else ''}")
    except ImportError:
        print("⚠️  pip install google-generativeai")
    except Exception as e:
        print(f"⚠️  AI Studio no conectado: {e}")


def _mensaje_soberania() -> str:
    bruto = os.environ.get("BUNKER_MONTO_BRUTO_EUR", "100.000,00 €").strip()
    gastos = os.environ.get("BUNKER_GASTOS_EUR", "2.000,00 €").strip()
    neto = os.environ.get("BUNKER_NETO_EUR", "98.000,00 €").strip()
    fecha = os.environ.get("BUNKER_HITO_FECHA", "9 de mayo").strip()
    return (
        f"TRYONYOU V10 — notificación de soberanía\n\n"
        f"Estado: sistema local arrancado (desarrollo)\n"
        f"Patente: {PATENT}\n"
        f"Entidad (ref.): SIREN {SIREN}\n\n"
        f"Hito (plantilla operativa — verificar en contabilidad real)\n"
        f"Fecha referencia: {fecha}\n"
        f"Monto bruto: {bruto}\n"
        f"Gastos operativos: -{gastos}\n"
        f"Neto a liquidar (referencia): {neto}\n\n"
        f"Timestamp: {datetime.now().isoformat(timespec='seconds')}"
    )


def _mensaje_soberania_pau_markdown() -> str:
    """Plantilla centinela PAU (Markdown clásico Telegram). Importes vía BUNKER_*."""
    bruto = os.environ.get("BUNKER_MONTO_BRUTO_EUR", "100.000,00 €").strip()
    gastos = os.environ.get("BUNKER_GASTOS_EUR", "2.000,00 €").strip()
    neto = os.environ.get("BUNKER_NETO_EUR", "98.000,00 €").strip()
    return (
        f"🏛️ *TRYONYOU V10: SOBERANÍA PAU ACTIVA*\n\n"
        f"✅ *Estado:* FALSITRYONES DESPEDIDOS\n"
        f"📑 *Licencia élite:* {PATENT}\n\n"
        f"💰 *Hito financiero: Le Bon Marché*\n"
        f"• Canon de licencia V10: {bruto}\n"
        f"• Comisión (Stripe Business): -{gastos}\n"
        f"• *Neto a liquidar (9 mayo):* {neto}\n\n"
        f"🔥 *A fuego: el búnker ha hablado.*"
    )


def _mensaje_telegram_bunker() -> str:
    if os.environ.get("TELEGRAM_FORMAT", "plain").strip().lower() == "markdown":
        return _mensaje_soberania_pau_markdown()
    return _mensaje_soberania()


def arranque_bunker() -> int:
    root = _root()
    ui = _mirror_ui(root)
    print(f"\n🚀 [{datetime.now().strftime('%H:%M:%S')}] Despliegue V10 — búnker soberanía")
    print("-" * 50)

    if not (ui / "package.json").is_file():
        print(f"❌ No hay package.json en la raíz ({root})")
        return 1

    _free_port_5173()
    print(
        "🧠 PAU / Robert Engine (ref. 99,7 %) — sincronización opcional con IA Studio…"
    )
    _pau_robert_mayo()

    if os.environ.get("SKIP_TELEGRAM", "").strip() not in ("1", "true", "yes"):
        print("📤 Notificación Telegram (si hay token + chat_id)…")
        enviar_telegram(_mensaje_telegram_bunker())
    else:
        print("ℹ️  SKIP_TELEGRAM=1 — sin envío.")

    print(f"\n🌐 Espejo: {VITE_URL}")
    try:
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(ui),
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("❌ npm no encontrado. Ejecuta npm install en la raíz del repo")
        return 1

    time.sleep(2.5)
    webbrowser.open(VITE_URL)
    print("⌛ Vite en marcha (Ctrl+C para detener).\n")
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
    raise SystemExit(arranque_bunker())
