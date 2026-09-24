"""
Registro de factura de referencia (demo consola). No genera PDF ni envía correo.

Patente: PCT/EP2025/067317

  python3 create_invoice_record_v10.py
  python3 create_invoice_record_v10.py --client "Le Bon Marché"
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime


def create_invoice_record(client_name: str = "Balmain") -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    invoice_id = f"DIV-{timestamp}-9900"

    print(f"--- GENERANDO FACTURA: {invoice_id} ---")
    print(f"Cliente: {client_name}")
    print("Estado: Pendiente de Envío SMTP")
    hint = os.environ.get("TRYONYOU_SMTP_NOTE", "").strip()
    if hint:
        print(f"Nota (entorno): {hint}")

    return invoice_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Registro de factura V10 (demo).")
    parser.add_argument("--client", default="Balmain", help="Nombre del cliente")
    args = parser.parse_args()
    create_invoice_record(client_name=args.client)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
