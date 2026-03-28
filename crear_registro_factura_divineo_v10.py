"""
Registro de factura Divineo V10 (demo consola) — ID DIV-YYYYMMDD-HHMM-9900.

Referencia operativa: no genera PDF ni envía correo; el envío SMTP queda en tu pipeline.

Patente: PCT/EP2025/067317

  python3 crear_registro_factura_divineo_v10.py
  INVOICE_CLIENT="Le Bon Marché" python3 crear_registro_factura_divineo_v10.py
"""

from __future__ import annotations

import os
from datetime import datetime


def create_invoice_record(client_name: str = "Balmain") -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    invoice_id = f"DIV-{timestamp}-9900"

    print(f"--- GENERANDO FACTURA: {invoice_id} ---")
    print(f"Cliente: {client_name}")
    print("Estado: Pendiente de envío SMTP")

    return invoice_id


def main() -> int:
    client = (os.environ.get("INVOICE_CLIENT", "") or "").strip() or "Balmain"
    create_invoice_record(client_name=client)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
