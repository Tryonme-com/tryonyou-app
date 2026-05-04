#!/usr/bin/env python3
"""
launcher.py — Genera la carpeta de trabajo TRYONYOU_ACTION_NOW y la plantilla
de correo para el mercado de París.

Uso:
    python launcher.py [--output-dir RUTA]

Sin argumentos escribe en ~/Desktop/TRYONYOU_ACTION_NOW.
Si el escritorio no está disponible (entornos sin GUI / sólo lectura),
escribe en TMPDIR/TRYONYOU_ACTION_NOW.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_OUTPUT_DIRNAME = "TRYONYOU_ACTION_NOW"
_EMAIL_FILENAME = "EMAIL_PARIS.txt"

_FR_EMAIL = """\
Objet : Opportunité de Partenariat : Réduire les retours clients de 40% - Pilote TryOnYou

À l'attention du Responsable de l'Innovation,

Le secteur du retail fait face à un taux de retour de 30-40%. TryOnYou a validé une
solution technique qui résout ce problème par une précision biométrique totale.

Nous cherchons un partenaire visionnaire pour un pilote de 30 jours : si nous ne
réduisons pas vos retours à zéro, le service ne vous est pas facturé.

Seriez-vous disponible pour une démonstration de 10 minutes cette semaine ?

Cordialement,
[Tu Nombre]
"""


def _default_output_dir() -> Path:
    """Retorna el directorio de salida predeterminado (Escritorio o /tmp)."""
    desktop = Path.home() / "Desktop"
    try:
        desktop.mkdir(parents=True, exist_ok=True)
        return desktop / _OUTPUT_DIRNAME
    except OSError:
        return Path(os.environ.get("TMPDIR", "/tmp")) / _OUTPUT_DIRNAME


def generate_action_kit(output_dir: str | Path | None = None) -> Path:
    """Crea el directorio de trabajo y escribe la plantilla de correo.

    Args:
        output_dir: Ruta al directorio de destino.  Si es ``None`` se usa
            ``~/Desktop/TRYONYOU_ACTION_NOW`` con fallback a ``/tmp``.

    Returns:
        El :class:`~pathlib.Path` del directorio creado.
    """
    dest = Path(output_dir) if output_dir is not None else _default_output_dir()
    dest.mkdir(parents=True, exist_ok=True)
    email_path = dest / _EMAIL_FILENAME
    email_path.write_text(_FR_EMAIL, encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera TRYONYOU_ACTION_NOW con la plantilla de correo para París.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directorio de salida (por defecto: ~/Desktop/TRYONYOU_ACTION_NOW).",
    )
    args = parser.parse_args(argv)

    dest = generate_action_kit(output_dir=args.output_dir)

    print(f"✅ TODO LISTO EN: {dest}")
    print("1. Abre la carpeta en tu escritorio.")
    print(f"2. Abre '{_EMAIL_FILENAME}', personaliza tu nombre.")
    print("3. Envía a tus contactos de la hoja CSV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
