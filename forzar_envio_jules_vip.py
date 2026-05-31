"""Alias de forzar_envio_jules_vip_safe. Uso: E50_GIT_PUSH=1 python3 forzar_envio_jules_vip.py"""

from __future__ import annotations

import sys

from forzar_envio_jules_vip_safe import forzar_envio_jules_vip_safe

if __name__ == "__main__":
    sys.exit(forzar_envio_jules_vip_safe())
