#!/usr/bin/env python3
"""
Preflight Stripe LIVE — comprueba clave secreta y payout BUNKER (no Test).

  - Rechaza sk_test_ en STRIPE_SECRET_KEY_FR / STRIPE_SECRET_KEY.
  - GET /v1/balance y, si existe BUNKER_SYNC_STRIPE_PAYOUT_ID, GET /v1/payouts/{id}.
  - No crea payouts nuevos (eso es operación tesorería en Dashboard o API dedicada).

Salida: JSON con livemode y http 200 esperado cuando el payout existe en Live.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError as e:
    print("pip install requests", file=sys.stderr)
    raise SystemExit(1) from e


def _sk() -> str:
    return (os.getenv("STRIPE_SECRET_KEY_FR") or os.getenv("STRIPE_SECRET_KEY") or "").strip()


def main() -> int:
    sk = _sk()
    if not sk:
        print(json.dumps({"ok": False, "error": "missing_stripe_secret"}, indent=2))
        return 2
    if sk.startswith("sk_test_"):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "stripe_test_key_rejected",
                    "hint": "Use sk_live_… en producción; po_… de test no existen en Live.",
                },
                indent=2,
            )
        )
        return 3

    auth = (sk, "")
    out: dict[str, object] = {"ok": True, "key_prefix": sk[:12] + "…"}

    r = requests.get("https://api.stripe.com/v1/balance", auth=auth, timeout=45)
    out["balance_http"] = r.status_code
    if r.status_code != 200:
        out["ok"] = False
        try:
            out["balance_error"] = r.json()
        except Exception:
            out["balance_error"] = r.text[:400]
        print(json.dumps(out, indent=2))
        return 4

    po = (os.getenv("BUNKER_SYNC_STRIPE_PAYOUT_ID") or "").strip()
    if po:
        pr = requests.get(f"https://api.stripe.com/v1/payouts/{po}", auth=auth, timeout=45)
        out["payout_id"] = po
        out["payout_http"] = pr.status_code
        try:
            pj = pr.json()
        except Exception:
            pj = {}
        out["payout_livemode"] = pj.get("livemode")
        if pr.status_code != 200:
            out["ok"] = False
            out["payout_error"] = pj or pr.text[:400]
        elif pj.get("livemode") is not True:
            out["ok"] = False
            out["payout_error"] = {"message": "payout_not_live_mode", "payload": pj}
    else:
        out["payout_id"] = None
        out["hint"] = "Defina BUNKER_SYNC_STRIPE_PAYOUT_ID con un po_… LIVE del Dashboard."

    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 5


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for name in (".env.production", ".env"):
        p = root / name
        if p.is_file():
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    raise SystemExit(main())
