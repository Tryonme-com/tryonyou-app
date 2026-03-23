"""
Alias de jules_push_final_safe: no ejecutes git add . ni push --force a ciegas.

Uso: E50_GIT_PUSH=1 python3 jules_push_final.py
"""

from __future__ import annotations

import sys

from jules_push_final_safe import jules_push_final_safe

if __name__ == "__main__":
    sys.exit(jules_push_final_safe())
