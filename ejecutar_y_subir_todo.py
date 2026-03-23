"""
Alias seguro: ejecutar_y_subir_todo() y ejecutar_y_subir_total() (typo del snippet original).

Uso: E50_GIT_PUSH=1 python3 ejecutar_y_subir_todo.py
"""

from __future__ import annotations

import sys

from ejecutar_y_subir_todo_safe import ejecutar_y_subir_todo_safe


def ejecutar_y_subir_todo() -> int:
    return ejecutar_y_subir_todo_safe()


def ejecutar_y_subir_total() -> int:
    """Nombre erróneo en if __name__ del snippet; misma función."""
    return ejecutar_y_subir_todo_safe()


if __name__ == "__main__":
    sys.exit(ejecutar_y_subir_todo())
