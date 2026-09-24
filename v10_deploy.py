"""
Punto único V10 → despliegue git acotado (mismo criterio que ejecutar_y_subir_todo_safe).

  E50_GIT_PUSH=1   obligatorio para git
  E50_PROJECT_ROOT ruta del repo
  E50_FORCE_PUSH=1 opcional
  E50_DEPLOY_PATHS=a,b  lista alternativa

python3 v10_deploy.py
"""

from __future__ import annotations

import sys

from ejecutar_y_subir_todo_safe import ejecutar_y_subir_todo_safe


def main() -> int:
    print("MAESTRO V10 — v10_deploy (bundle explícito, sin git add .)")
    return ejecutar_y_subir_todo_safe()


if __name__ == "__main__":
    sys.exit(main())
