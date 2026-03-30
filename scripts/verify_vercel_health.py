"""
Comprueba que una URL Vercel (u otra) responde por HTTP — no mide precisión
física de escaneo (p. ej. 0,08 mm).

  export VERIFY_VERCEL_URL='https://tu-proyecto.vercel.app/'
  python3 scripts/verify_vercel_health.py

  python3 scripts/verify_vercel_health.py https://...

Patente (ref. proyecto): PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    url = (os.environ.get("VERIFY_VERCEL_URL") or "").strip()
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
    if not url:
        print(
            "Define VERIFY_VERCEL_URL o pasa la URL como argumento.",
            file=sys.stderr,
        )
        return 2
    if not url.startswith(("http://", "https://")):
        url = "https://" + url.lstrip("/")

    print(f"[verify_vercel_health] GET {url!r}")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TryOnYou-verify-vercel-health/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
            body = r.read(8000)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Red: {e}", file=sys.stderr)
        return 1

    print(f"  OK status={code} bytes_leídos≥{len(body)}")
    return 0 if 200 <= code < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
