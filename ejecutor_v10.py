"""
Ejecutor V10 — demostración en terminal: cumplimiento → factura PDF → Telegram → Vite.

  export TELEGRAM_BOT_TOKEN='…'
  export TELEGRAM_CHAT_ID='…'
  export TELEGRAM_FORMAT=markdown          # opcional
  export SKIP_TELEGRAM=1                   # solo demo local sin Telegram
  export TRYONYOU_IBAN='FR76…'             # opcional (factura)

  python3 ejecutor_v10.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

from datetime import datetime

from factura_proforma_v10 import generar_factura_pdf
from protocolo_v10_despliegue import ejecutar_despliegue


def _banner_cumplimiento_y_factura() -> None:
    print()
    print("=" * 58)
    print("  TRYONYOU V10 — UNIDAD DE PRODUCCIÓN (demo terminal)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 58)
    print()
    print("  1) Check de cumplimiento (RGPD / SIRET) antes de documentar importes.")
    print("  2) Generación de factura proforma PDF (referencia operativa).")
    print("  3) Notificación centinela (Telegram) + Espejo digital (Vite :5173).")
    print()
    print("  Referencia canon entrada (narrativa B2B): 100.000,00 €")
    print("  Total neto en proforma PDF (ejemplo): 126.000,00 € — revisar en sistemas reales.")
    print()


def main() -> int:
    _banner_cumplimiento_y_factura()
    generar_factura_pdf()
    return ejecutar_despliegue()


if __name__ == "__main__":
    raise SystemExit(main())
