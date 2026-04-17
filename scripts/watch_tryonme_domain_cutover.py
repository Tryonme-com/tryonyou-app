"""
Monitor corto para detectar cutover de dominio a Vercel.

Uso:
  python3 scripts/watch_tryonme_domain_cutover.py
  WATCH_DOMAIN=tryonme.app WATCH_TRIES=120 WATCH_SLEEP=5 python3 scripts/watch_tryonme_domain_cutover.py

Éxito cuando:
  - respuesta no viene de `server: nginx`, y
  - status HTTP es 2xx/3xx.
"""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _head(domain: str) -> tuple[int, str]:
    url = f"https://{domain}"
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=20) as response:
        code = int(response.status)
        server = response.headers.get("server", "").strip().lower()
        return code, server


def main() -> int:
    domain = os.getenv("WATCH_DOMAIN", "tryonme.app").strip() or "tryonme.app"
    tries = int(os.getenv("WATCH_TRIES", "60"))
    sleep_s = float(os.getenv("WATCH_SLEEP", "5"))

    print(f"[watch] domain={domain} tries={tries} sleep={sleep_s}s")
    for i in range(1, tries + 1):
        ts = _now()
        try:
            code, server = _head(domain)
            print(f"{ts} try={i} code={code} server={server or 'unknown'}")
            # nginx detectado: sigue apuntando a origen externo.
            if server != "nginx" and 200 <= code < 400:
                print(f"[watch] CUTOVER_OK domain={domain} code={code} server={server}")
                return 0
        except urllib.error.HTTPError as e:
            server = (e.headers.get("server", "") if e.headers else "").strip().lower()
            print(f"{ts} try={i} code={e.code} server={server or 'unknown'}")
            if server != "nginx" and 200 <= e.code < 400:
                print(f"[watch] CUTOVER_OK domain={domain} code={e.code} server={server}")
                return 0
        except OSError as e:
            print(f"{ts} try={i} network_error={e}")

        time.sleep(sleep_s)

    print(f"[watch] CUTOVER_PENDING domain={domain} (no switch detected yet)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
