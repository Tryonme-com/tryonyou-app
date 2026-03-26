"""
Jules V10 — purga y consolidación de soberanía (cachés y residuos locales).

Elimina carpetas de caché conocidas bajo la raíz del repo; no borra node_modules completo.

Patente: PCT/EP2025/067317

  python3 bunker_cleaner_v10.py
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parent


def _should_skip_path(p: Path, root: Path) -> bool:
    try:
        rel = p.relative_to(root)
    except ValueError:
        return True
    parts = set(rel.parts)
    if ".venv" in parts or "venv" in parts:
        return True
    if ".git" in parts:
        return True
    return False


class BunkerCleaner:
    def __init__(self) -> None:
        self.root = _root()
        self.siret = "94361019600017"
        self.patent = "PCT/EP2025/067317"
        self.critical_files = ["unificar_v10.py", "supercommit_max.sh", "image.png"]

    def _remove_dir_if_exists(self, rel: str) -> None:
        path = self.root / rel
        if path.is_dir():
            shutil.rmtree(path)
            print(f"🗑️ Eliminado: {rel}")

    def _purge_pycache_under_root(self) -> None:
        for p in sorted(self.root.rglob("__pycache__"), key=lambda x: len(x.parts), reverse=True):
            if not p.is_dir() or _should_skip_path(p, self.root):
                continue
            shutil.rmtree(p)
            try:
                rel = p.relative_to(self.root)
            except ValueError:
                rel = p
            print(f"🗑️ Eliminado: {rel}")

    def ejecutar_limpieza(self) -> str:
        os.chdir(self.root)
        print("🧹 Iniciando limpieza de residuos técnicos (cachés)...")

        print(f"✅ [Jules]: Sello operativo — rama de trabajo: {self.root}")
        print(f"   Patente (ref.): {self.patent} · SIRET (ref.): {self.siret}")

        for name in self.critical_files:
            p = self.root / name
            print(f"   📌 Activo: {name}" if p.is_file() else f"   ⚠️  No hallado: {name}")

        trash_rel = [
            ".next",
            "mirror_ui/.next",
            "node_modules/.cache",
            "mirror_ui/node_modules/.cache",
            "temp_logs",
        ]
        for rel in trash_rel:
            self._remove_dir_if_exists(rel)

        self._purge_pycache_under_root()

        print(f"💎 Referencia soberanía / trazabilidad: SIRET {self.siret}")

        return "✨ Búnker limpio. JULES enfocado 100% en la liquidez de Bpifrance."


if __name__ == "__main__":
    jules = BunkerCleaner()
    print(jules.ejecutar_limpieza())
