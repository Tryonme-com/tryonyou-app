#!/usr/bin/env python3
"""
Imprime la URL de Checkout inaugural (API local / mismas vars que Vercel).

  export STRIPE_SECRET_KEY=sk_live_...
  python3 scripts/print_inauguration_checkout_url.py

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_API = _ROOT / "api"
for p in (_ROOT, _API):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

from stripe_inauguration import create_inauguration_checkout_session


def main() -> None:
    origin = (os.getenv("STRIPE_CHECKOUT_ORIGIN") or "https://tryonyou.app").strip()
    payload, code = create_inauguration_checkout_session(origin)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if code == 200 and payload.get("url"):
        print("\n--- CHECKOUT URL ---\n" + payload["url"] + "\n", file=sys.stderr)
    sys.exit(0 if code == 200 else 1)


if __name__ == "__main__":
    main()
