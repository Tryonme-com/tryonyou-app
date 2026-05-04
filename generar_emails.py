"""
Generador de secuencia de emails comerciales — TryOnYou.

Genera un CSV con asuntos y cuerpos de email listos para su revisión y envío.
El archivo de salida se escribe en /tmp (o TMPDIR) para compatibilidad con
despliegues de sólo lectura (p. ej. Vercel).

  python3 generar_emails.py

Salida: /tmp/secuencia_emails.csv (o ruta alternativa si TMPDIR está definido)

Bajo Protocolo de Soberanía V10 - Founder: Rubén
Patente: PCT/EP2025/067317
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

# Texto "puente" para gestionar preguntas sobre licenciamiento / precios
BRIDGE_TEXT = (
    "Respecto a la fase post-prueba: nuestro modelo de implementación se diseña "
    "a medida basándonos en los KPIs de tu operativa. Por ello, preferimos tratar "
    "los detalles de licenciamiento en nuestra reunión de estrategia, garantizando "
    "así que la solución esté alineada con vuestros objetivos específicos de retorno "
    "de inversión (ROI)."
)

# Secuencia de emails comerciales
EMAILS: list[dict[str, str]] = [
    {
        "Asunto": "Reducción del 30-40% en devoluciones - Propuesta TryOnYou",
        "Cuerpo": (
            f"Hola, he analizado vuestras cifras actuales de devoluciones. "
            f"TryOnYou permite una auditoría biométrica de 0.08mm para corregir "
            f"patrones. Ofrecemos 30 días de prueba gratuita. {BRIDGE_TEXT}"
        ),
    },
    {
        "Asunto": "Datos biométricos y eficiencia en producto",
        "Cuerpo": (
            f"La industria está cambiando: o nos adaptamos o desaparecemos. "
            f"Con nuestra tecnología, los datos dejan de ser estáticos y pasan "
            f"a ser decisiones de producto. ¿Hablamos? {BRIDGE_TEXT}"
        ),
    },
]

# Directorio de salida: /tmp o TMPDIR para compatibilidad con entornos read-only
_TMP = Path(os.environ.get("TMPDIR", "/tmp"))
OUTPUT_PATH = _TMP / "secuencia_emails.csv"


def generar_secuencia(output_path: Path = OUTPUT_PATH) -> Path:
    """Escribe la secuencia de emails en un CSV y devuelve la ruta del archivo."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, mode="w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["Asunto", "Cuerpo"])
            writer.writeheader()
            writer.writerows(EMAILS)
    except OSError as exc:
        print(f"⚠️  No se pudo escribir en {output_path}: {exc}")
        raise
    return output_path


def main() -> int:
    path = generar_secuencia()
    print(f"✅ Archivo '{path}' generado exitosamente ({len(EMAILS)} emails).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
