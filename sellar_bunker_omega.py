"""
Sello operativo (log + comprobación de env). No escanea STATION F ni redes reales.

  E50_PROJECT_ROOT — raíz del proyecto (solo si E50_WRITE_SEAL=1)
  E50_WRITE_SEAL=1 — escribe src/data/omega_seal.json con marca temporal y resumen env

python3 sellar_bunker_omega.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [SECURITY_CORE] | %(message)s",
    stream=sys.stdout,
)


def _present(*names: str) -> bool:
    return any(os.environ.get(n, "").strip() for n in names)


def _env_snapshot() -> dict[str, str]:
    return {
        "stripe_secret": "ok"
        if _present(
            "STRIPE_SECRET_KEY_FR",
            "E50_STRIPE_SECRET_KEY_FR",
            "STRIPE_SECRET_KEY",
            "E50_STRIPE_SECRET_KEY",
        )
        else "missing",
        "stripe_publishable": "ok"
        if _present(
            "VITE_STRIPE_PUBLIC_KEY_FR",
            "E50_VITE_STRIPE_PUBLIC_KEY_FR",
            "VITE_STRIPE_PUBLIC_KEY",
            "E50_VITE_STRIPE_PUBLIC_KEY",
        )
        else "missing",
        "smtp": "ok"
        if _present("EMAIL_USER", "E50_SMTP_USER") and _present("EMAIL_PASS", "E50_SMTP_PASS")
        else "missing",
    }


def sellar_bunker_omega() -> int:
    logging.info("Protocolo de sellado OMEGA (diagnóstico local, sin red)...")

    labels = {
        "BIOMETRIC_PRECISION": "claim_UI_only",
        "STRIKE_GATEWAY": "verify_VITE_and_backend",
        "JULES_SMTP": "see_smtp_line_below",
        "PARIS_RADAR": "not_a_network_scan",
    }
    for key, value in labels.items():
        logging.info("Etiqueta %s: %s", key, value)
        time.sleep(0.15)

    snap = _env_snapshot()
    logging.info("SMTP (EMAIL_*): %s", snap["smtp"])
    logging.info("Stripe sk: %s | pk VITE: %s", snap["stripe_secret"], snap["stripe_publishable"])
    logging.info(
        "No hay socket ni perímetro real: configura alertas (Stripe webhooks, uptime) en producción."
    )

    if os.environ.get("E50_WRITE_SEAL", "").strip().lower() in ("1", "true", "yes", "on"):
        os.makedirs(ROOT, exist_ok=True)
        data_dir = os.path.join(ROOT, "src", "data")
        os.makedirs(data_dir, exist_ok=True)
        payload = {
            "_note": "Instantané local; pas un audit de sécurité.",
            "sealed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "env_snapshot": snap,
        }
        path = os.path.join(data_dir, "omega_seal.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        logging.info("Sello escrito: %s", os.path.relpath(path, ROOT))

    print("\n" + "=" * 60)
    print("TRYONYOU — diagnóstico OMEGA V10 (local)")
    print("Revisa Vercel, Stripe y SMTP antes de afirmar producción.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(sellar_bunker_omega())
