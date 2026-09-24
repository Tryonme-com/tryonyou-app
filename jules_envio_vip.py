"""
Alias de jules_envio_vip_safe: JSON con _meta + git acotado (no git add .).

Uso: python3 jules_envio_vip.py
     E50_GIT_PUSH=1 python3 jules_envio_vip.py
"""

from __future__ import annotations

import sys

from jules_envio_vip_safe import jules_envio_vip_safe

if __name__ == "__main__":
    sys.exit(jules_envio_vip_safe())
