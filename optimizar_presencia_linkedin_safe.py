"""
Escribe fragmento Open Graph (LinkedIn / redes) bajo src/seo/; git opcional y acotado.

El snippet original no persistía og_metadata en disco y hacía git add . + --force.

Variables opcionales (solo sustituyen al generar el archivo):
  E50_OG_TITLE, E50_OG_DESCRIPTION, E50_OG_IMAGE_URL, E50_OG_URL

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1, E50_FORCE_PUSH=1 opcional.

Pega el contenido de linkedin_og_fragment.html en el <head> de tu index.html (Vite/Next).

Ejecutar: python3 optimizar_presencia_linkedin_safe.py
"""

from __future__ import annotations

import html
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

DEFAULT_TITLE = "TryOnYou France: L'Infrastructure de Précision"
DEFAULT_DESC = (
    "Élimination des retours retail via le Double Numérique Biométrique. "
    "Brevet PCT/EP2025/067317."
)
DEFAULT_IMAGE = "https://tryonyou.app/assets/branding/pau_luxury_banner.png"

GIT_PATHS = [
    "src/seo/linkedin_og_fragment.html",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _meta_fragment() -> str:
    title = os.environ.get("E50_OG_TITLE", "").strip() or DEFAULT_TITLE
    desc = os.environ.get("E50_OG_DESCRIPTION", "").strip() or DEFAULT_DESC
    image = os.environ.get("E50_OG_IMAGE_URL", "").strip() or DEFAULT_IMAGE
    url = os.environ.get("E50_OG_URL", "").strip()
    lines = [
        "<!-- Open Graph / LinkedIn — copiar dentro de <head> -->",
        f'<meta property="og:title" content="{html.escape(title)}" />',
        '<meta property="og:type" content="website" />',
    ]
    if url:
        lines.append(f'<meta property="og:url" content="{html.escape(url)}" />')
    lines.extend(
        [
            f'<meta property="og:image" content="{html.escape(image)}" />',
            f'<meta property="og:description" content="{html.escape(desc)}" />',
            '<meta name="twitter:card" content="summary_large_image" />',
        ]
    )
    return "\n".join(lines) + "\n"


def optimizar_presencia_linkedin_safe() -> int:
    print("💎 Generando fragmento Open Graph (LinkedIn / redes)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    seo_dir = os.path.join(ROOT, "src", "seo")
    os.makedirs(seo_dir, exist_ok=True)
    path = os.path.join(seo_dir, "linkedin_og_fragment.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_meta_fragment())

    print(f"✅ {os.path.relpath(path, ROOT)}")
    print("ℹ️  linkedin:owner no es meta estándar para el crawler; usa og:* y URL/imagen públicas.")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "STRATEGY: LinkedIn Social Graph Optimization for Paris HQ Access",
        ],
        cwd=ROOT,
    )
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado. Valida la imagen og:image (200 OK, tamaño razonable).")
    return 0


if __name__ == "__main__":
    sys.exit(optimizar_presencia_linkedin_safe())
