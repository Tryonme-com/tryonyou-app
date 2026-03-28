"""
Rescue DNS (Porkbun) — nameservers, MX y registro A para Vercel.

Nunca pegues claves en el repo. Define antes de ejecutar:

  export PORKBUN_API_KEY='pk1_...'
  export PORKBUN_SECRET_KEY='sk1_...'
  export PORKBUN_DOMAIN='tryonyou.app'   # opcional (default abajo)

  pip install requests
  python3 rescue_dns.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
import time

import requests

BASE_URL = "https://porkbun.com/api/json/v3"
DEFAULT_DOMAIN = "tryonyou.app"
DEFAULT_NS = [
    "curiosity.porkbun.com",
    "marvin.porkbun.com",
    "mabel.porkbun.com",
    "emmett.porkbun.com",
]


def _auth() -> dict[str, str]:
    api = os.environ.get("PORKBUN_API_KEY", "").strip()
    sec = os.environ.get("PORKBUN_SECRET_KEY", "").strip()
    if not api or not sec:
        print(
            "Define PORKBUN_API_KEY y PORKBUN_SECRET_KEY en el entorno.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return {"apiKey": api, "secretKey": sec}


def fix() -> None:
    domain = os.environ.get("PORKBUN_DOMAIN", DEFAULT_DOMAIN).strip().strip(".")
    auth = _auth()

    print(f"📡 1/3 Recuperando mando de {domain}...")
    ns_data = {**auth, "ns": DEFAULT_NS}
    res = requests.post(
        f"{BASE_URL}/domain/updateNS/{domain}",
        json=ns_data,
        timeout=60,
    )
    print(f"   Status: {res.status_code} {res.text[:500]}")

    time.sleep(2)

    print(f"📩 2/3 Restaurando email (MX) en {domain}...")
    mx1 = {**auth, "type": "MX", "name": "", "content": "fwd1.porkbun.com", "prio": "10"}
    mx2 = {**auth, "type": "MX", "name": "", "content": "fwd2.porkbun.com", "prio": "20"}

    r_mx1 = requests.post(
        f"{BASE_URL}/dns/create/{domain}",
        json=mx1,
        timeout=60,
    )
    r_mx2 = requests.post(
        f"{BASE_URL}/dns/create/{domain}",
        json=mx2,
        timeout=60,
    )
    print(f"   MX1: {r_mx1.status_code} {r_mx1.text[:200]}")
    print(f"   MX2: {r_mx2.status_code} {r_mx2.text[:200]}")

    print("🌐 3/3 Vinculando web (A @) a Vercel…")
    a_rec = {**auth, "type": "A", "name": "", "content": "76.76.21.21"}
    r_a = requests.post(
        f"{BASE_URL}/dns/create/{domain}",
        json=a_rec,
        timeout=60,
    )
    print(f"   A: {r_a.status_code} {r_a.text[:200]}")

    print("\n✅ Operación enviada. El correo puede tardar unos minutos en propagarse.")
    print("Si había registros duplicados, revisa el panel Porkbun.")


if __name__ == "__main__":
    fix()
