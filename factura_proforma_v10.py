"""
Factura proforma PDF (referencia auditoría). IBAN vía entorno, no en código.

  export TRYONYOU_IBAN='FR76…'   # opcional; si falta, usa marcador __CONFIGURAR__

  python3 factura_proforma_v10.py
"""

from __future__ import annotations

import os
from pathlib import Path

from fpdf import FPDF

SIRET = "94361019600017"
PATENT = "PCT/EP2025/067317"


def generar_factura_pdf(
    *,
    output_path: str | Path | None = None,
    siret: str = SIRET,
    iban: str | None = None,
    total_net: float = 126_000.00,
    due_date: str = "2026-05-09",
) -> Path:
    iban = (iban or os.environ.get("TRYONYOU_IBAN", "")).strip() or "__CONFIGURAR_IBAN__"
    out = Path(
        output_path
        or os.environ.get("TRYONYOU_FACTURA_PATH", "")
        or Path.cwd() / "proforma_tryonyou_v10.pdf"
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"📄 Generando factura proforma vinculada al SIRET {siret}…")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "TRYONYOU SAS — Factura proforma (referencia)", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.ln(4)
    pdf.multi_cell(
        0,
        6,
        f"SIRET: {siret}\n"
        f"Patente (ref.): {PATENT}\n"
        f"IBAN (indicativo): {iban}\n"
        f"Total neto (referencia): {total_net:,.2f} EUR\n"
        f"Vencimiento (referencia): {due_date}\n\n"
        "Documento generado para trazabilidad B2B / auditoría. "
        "Sustituir IBAN real vía TRYONYOU_IBAN antes de uso formal.",
    )

    pdf.output(str(out))
    print(f"✅ PDF guardado: {out.resolve()}")
    return out


if __name__ == "__main__":
    generar_factura_pdf()
