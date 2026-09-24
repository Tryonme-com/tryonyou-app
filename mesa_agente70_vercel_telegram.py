"""Mesa Redonda — Agente 70: comprobar 6 dominios (proxy HTTP de «en verde») y avisar a Telegram.

No sustituye el panel de Vercel (DNS / asignación de dominios); valida que cada host responde HTTPS.

  export TELEGRAM_BOT_TOKEN=…   # o TELEGRAM_TOKEN
  export TELEGRAM_CHAT_ID=…
  # opcional — hosts separados por coma (exactamente los que Vercel tenga asignados al proyecto)
  export MESA_VERCEL_DOMAIN_CHECK='tryonme.app,abvetos.com,tryonme.com,tryonme.org,tryonyou.app,api.tryonyou.app'

  python3 mesa_agente70_vercel_telegram.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

import requests

STAMP_C = "@CertezaAbsoluta"
STAMP_L = "@lo+erestu"
PATENT = "PCT/EP2025/067317"
PROTOCOL = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"

# Red soberana documentada en el proyecto (6 hosts); override con MESA_VERCEL_DOMAIN_CHECK
DEFAULT_HOSTS = (
    "tryonme.app",
    "abvetos.com",
    "tryonme.com",
    "tryonme.org",
    "tryonyou.app",
    "api.tryonyou.app",
)


def _hosts() -> list[str]:
    raw = (os.environ.get("MESA_VERCEL_DOMAIN_CHECK") or "").strip()
    if raw:
        return [h.strip().lower().rstrip("/") for h in raw.split(",") if h.strip()]
    return list(DEFAULT_HOSTS)


def probe_host(host: str) -> tuple[bool, str]:
    url = f"https://{host}/"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TryOnYou-MesaAgente70/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            code = r.status
            ok = 200 <= code < 400
            return ok, f"HTTP {code}"
    except urllib.error.HTTPError as e:
        return 200 <= e.code < 400, f"HTTP {e.code}"
    except OSError as e:
        return False, str(e)[:200]


def verify_domains() -> tuple[list[tuple[str, bool, str]], bool]:
    results: list[tuple[str, bool, str]] = []
    all_ok = True
    for host in _hosts():
        ok, detail = probe_host(host)
        results.append((host, ok, detail))
        if not ok:
            all_ok = False
        status = "OK" if ok else "FALLO"
        print(f"  [{status}] {host} — {detail}")
    return results, all_ok


def _telegram_send(text: str) -> bool:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(
            "Sin TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) / TELEGRAM_CHAT_ID: no se envía "
            "señal.",
            file=sys.stderr,
        )
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat, "text": text}, timeout=30)
    if not r.ok:
        print(r.status_code, r.text[:500], file=sys.stderr)
        return False
    return True


def main() -> int:
    print("--- MESA REDONDA | AGENTE 70 | verificación dominios (HTTP) ---")
    print(f"UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    hosts = _hosts()
    print(f"Hosts ({len(hosts)}): {', '.join(hosts)}")

    results, all_ok = verify_domains()

    n = len(hosts)
    lines = [
        "AGENTE70 — Mesa Redonda V10",
        "Señal para RUBENSANZBUROBOT (éxito operativo búnker París Guy Moquet).",
        "",
        f"Protocolo V10: {n} dominio(s) en rastreo soberano (chequeo HTTPS Agente 70).",
        "Verificación HTTPS (proxy de disponibilidad; confirmar panel Vercel):",
    ]
    for host, ok, detail in results:
        lines.append(f"• {host}: {'VERDE' if ok else 'ROJO'} ({detail})")
    lines.extend(
        [
            "",
            f"Búnker Guy Moquet (París): técnicamente operativo según chequeo. {PROTOCOL}",
            f"{STAMP_C} {STAMP_L} {PATENT}",
        ]
    )
    body = "\n".join(lines)

    if not _telegram_send(body):
        return 1 if all_ok else 2
    print("--- Señal Telegram enviada (RUBENSANZBUROBOT / chat configurado). ---")
    return 0 if all_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
