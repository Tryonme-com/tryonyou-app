from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path
from typing import Sequence

# Archivos clave que validan la PoC técnica.
ASSETS_TO_INCLUDE = (
    "🔍 VALIDACIÓN DE PILOTO - TRYONYOU.pdf",
    "Estructura de Subtítulos y Metadatos para Traducción.pdf",
)

EMAIL_TEMPLATE = """\
SUBJECT: Partnership Opportunity: TryOnYou Technical Pilot

Dear Innovation Manager,

TryOnYou is preparing a focused retail pilot for AI-assisted biometric fit
guidance and customer confidence at the point of purchase.

We are looking for a forward-thinking partner to validate the workflow against
real catalogue, sizing and return-friction data. The attached package includes
the technical validation material and the project manifesto for review.

Would you be available for a 10-minute demo this week to see the system in
action and define the pilot KPIs together?

Best regards,
[Your Name]
TryOnYou - Paris 2026
"""


def default_export_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if desktop.is_dir() and os.access(desktop, os.W_OK):
        return desktop / "TRYONYOU_COMMERCIAL_PACKAGE"
    return Path(tempfile.gettempdir()) / "TRYONYOU_COMMERCIAL_PACKAGE"


def prepare_package(
    export_dir: str | Path | None = None,
    source_dir: str | Path | None = None,
    assets: Sequence[str] = ASSETS_TO_INCLUDE,
) -> Path:
    destination = Path(export_dir) if export_dir is not None else default_export_dir()
    source_root = Path(source_dir) if source_dir is not None else Path.cwd()
    destination.mkdir(parents=True, exist_ok=True)

    print("Preparando paquete comercial...")

    for asset in assets:
        asset_path = source_root / asset
        if asset_path.is_file():
            shutil.copy2(asset_path, destination / asset_path.name)
            print(f"Anadido: {asset}")
        else:
            print(f"No encontrado (omitido): {asset}")

    with (destination / "EMAIL_TEMPLATE.txt").open("w", encoding="utf-8") as f:
        f.write(EMAIL_TEMPLATE)

    print(f"\nPAQUETE LISTO EN: {destination}")
    print("Pasos siguientes:")
    print("1. Abre la carpeta generada.")
    print("2. Abre 'EMAIL_TEMPLATE.txt', personaliza tu nombre y cópialo.")
    print("3. Envía el email a los Innovation Managers desde tu cuenta profesional.")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepara el paquete comercial de TryOnYou.")
    parser.add_argument("--output-dir", help="Directorio de salida del paquete.")
    args = parser.parse_args()

    prepare_package(export_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
