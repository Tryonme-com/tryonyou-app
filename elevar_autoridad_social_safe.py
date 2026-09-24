"""
Genera src/seo/authority_social_metadata.html (Open Graph + robots para copiar en <head>).

No usa linkedin:owner (no es meta estándar del preview de LinkedIn). Git opcional, un solo archivo.

Variables opcionales:
  E50_OG_SITE_NAME, E50_OG_TITLE_AUTH, E50_OG_DESC_AUTH, E50_ROBOTS_CONTENT

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1, E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 elevar_autoridad_social_safe.py
"""

from __future__ import annotations

import html
import logging
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [AUTH_SOCIAL] | %(message)s",
    stream=sys.stdout,
)

DEFAULT_SITE = "TryOnYou France - L'Usine de Certitude"
DEFAULT_TITLE = "Infrastructure Biométrique pour le Luxe International"
DEFAULT_DESC = (
    "Solution Zero-Retour basée sur la physique textile réelle. Licence Enterprise PCT/EP2025."
)
DEFAULT_ROBOTS = "index, follow"

GIT_PATHS = [
    "src/seo/authority_social_metadata.html",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        logging.error("%s", e)
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _fragment() -> str:
    site = os.environ.get("E50_OG_SITE_NAME", "").strip() or DEFAULT_SITE
    title = os.environ.get("E50_OG_TITLE_AUTH", "").strip() or DEFAULT_TITLE
    desc = os.environ.get("E50_OG_DESC_AUTH", "").strip() or DEFAULT_DESC
    robots = os.environ.get("E50_ROBOTS_CONTENT", "").strip() or DEFAULT_ROBOTS
    lines = [
        "<!-- Autorité sociale / LinkedIn — coller dans <head> (compléter og:image / og:url ailleurs) -->",
        f'<meta property="og:site_name" content="{html.escape(site)}" />',
        f'<meta property="og:title" content="{html.escape(title)}" />',
        f'<meta property="og:description" content="{html.escape(desc)}" />',
        '<meta property="og:type" content="website" />',
        f'<meta name="robots" content="{html.escape(robots)}" />',
    ]
    return "\n".join(lines) + "\n"


def elevar_autoridad_social_safe() -> int:
    logging.info("Calibrando fragmento metadatos (París / visibilité)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    seo = os.path.join(ROOT, "src", "seo")
    os.makedirs(seo, exist_ok=True)
    path = os.path.join(seo, "authority_social_metadata.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_fragment())

    logging.info("Escrito %s", os.path.relpath(path, ROOT))

    if not _on("E50_GIT_PUSH"):
        logging.info("Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        logging.info("No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        logging.error("git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "STRATEGY: LinkedIn authority injector for Paris HQ visibility",
        ],
        cwd=ROOT,
    )
    if rc not in (0, 1):
        logging.error("git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        logging.error("git push falló")
        return 1

    print("\n" + "=" * 60)
    print("LINKEDIN / SEO FRAGMENT: generado y pusheado si aplica")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(elevar_autoridad_social_safe())
