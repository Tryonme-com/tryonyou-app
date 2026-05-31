"""Puente Colaborador → Make.com → Shopify / hojas de registro.

Variable de entorno: MAKE_WEBHOOK_URL = URL del módulo Custom webhook del escenario
(ej. https://hook.eu2.make.com/...), NO la URL del dashboard (eu2.make.com/organization/5247214/...).

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime, timezone
from typing import Any

import requests


class ShopifyMakeBridge:
    def __init__(self) -> None:
        self.webhook_url = os.getenv("MAKE_WEBHOOK_URL", "").strip()
        self.patent = "PCT/EP2025/067317"
        self.siret = "94361019600017"

    def sync_colaborador(self, datos_colaborador: dict[str, Any]) -> bool:
        """Envía el colaborador a Make para distribución a Shopify y log (Sheets/Excel)."""
        nombre = datos_colaborador.get("nombre", "")
        print(f"[JULES] Sincronizando colaborador: {nombre}")

        if not self.webhook_url:
            print("Falta MAKE_WEBHOOK_URL en el entorno.", file=sys.stderr)
            return False

        rcs = str(datos_colaborador.get("rcs", "")).strip()
        rcs_hash = hashlib.sha256(rcs.encode("utf-8")).hexdigest()

        payload = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "founder": "Rubén Espinar Rodríguez",
            "patente": self.patent,
            "siret_bunker": self.siret,
            "colaborador": datos_colaborador,
            "security_hash": rcs_hash,
            "protocolo": "V10_OMEGA",
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
        except requests.RequestException as e:
            print(f"Red/Make: {e}", file=sys.stderr)
            return False

        if response.status_code != 200:
            print(response.status_code, response.text[:500], file=sys.stderr)
            return False
        return True

    def consolidar_inventario_vip(self) -> None:
        """Reservado: reglas SAC Museum / Cero Falsivitis en Shopify vía Make u otro conector."""
        print("[LISTOS] Validación inventario VIP (placeholder — conectar módulo Make/Shopify).")


def main() -> int:
    bridge = ShopifyMakeBridge()
    test_colab = {
        "nombre": "Lafayette Artisan",
        "rcs": "802345678",
        "pieza": "Vestido Oro Líquido",
    }
    if not bridge.webhook_url:
        print(
            "Prueba omitida: export MAKE_WEBHOOK_URL='https://hook.eu2.make.com/…'\n"
            "Luego: python3 shopify_make_bridge.py",
            file=sys.stderr,
        )
        return 1
    ok = bridge.sync_colaborador(test_colab)
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
