import os
import shutil
import tempfile

# Configuración del paquete de venta
_DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop", "TRYONYOU_COMMERCIAL_PACKAGE")
EXPORT_DIR = _DESKTOP if os.access(os.path.dirname(_DESKTOP) or ".", os.W_OK) else os.path.join(
    tempfile.gettempdir(), "TRYONYOU_COMMERCIAL_PACKAGE"
)

# Archivos clave que validan tu PoC técnica
ASSETS_TO_INCLUDE = [
    "🔍 VALIDACIÓN DE PILOTO - TRYONYOU.pdf",
    "Estructura de Subtítulos y Metadatos para Traducción.pdf",
]

EMAIL_TEMPLATE = """\
ASUNTO: Partnership Opportunity: Reducing Retail Returns by 40% - TryOnYou Pilot

Dear Innovation Manager,

The fashion retail industry currently faces a 30-40% return rate, creating significant operational waste.
At TryOnYou, we have successfully validated a PoC that solves this through AI-driven
biometric matching and emotional intelligence, ensuring a 99.7% fit guarantee.

We are looking for a forward-thinking partner to launch a 30-day pilot.
If we do not reduce your return rates to zero, there is no cost.

Please find attached our technical validation and project manifesto.
Are you available for a 10-minute demo this week to see the system in action?

Best regards,
[Tu Nombre]
TryOnYou - Paris 2026
"""


def prepare_package() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)

    print("📦 Preparando paquete comercial...")

    # 1. Copiar los documentos clave validados
    for asset in ASSETS_TO_INCLUDE:
        if os.path.exists(asset):
            shutil.copy(asset, EXPORT_DIR)
            print(f"✅ Añadido: {asset}")
        else:
            print(f"⚠️  No encontrado (omitido): {asset}")

    # 2. Generar el archivo de texto con el cuerpo del email profesional
    with open(os.path.join(EXPORT_DIR, "EMAIL_TEMPLATE.txt"), "w", encoding="utf-8") as f:
        f.write(EMAIL_TEMPLATE)

    print(f"\n🚀 PAQUETE LISTO EN: {EXPORT_DIR}")
    print("Pasos siguientes:")
    print("1. Abre la carpeta creada en tu escritorio.")
    print("2. Abre 'EMAIL_TEMPLATE.txt', personaliza tu nombre y cópialo.")
    print("3. Envía el email a los Innovation Managers desde tu cuenta profesional.")


def main() -> int:
    prepare_package()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
