"""
Jules V10 — purga y consolidación de soberanía (limpieza local de artefactos).

Elimina solo bajo la raíz del repo: .next, node_modules/.cache, __pycache__ (recursivo),
temp_logs. No borra node_modules completo ni .env.

Patente: PCT/EP2025/067317

  python3 bunker_cleaner_v10.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parent


class BunkerCleaner:
    def __init__(self) -> None:
        self.siret = "94361019600017"
        self.patent = "PCT/EP2025/067317"
        self.critical_files = ["unificar_v10.py", "supercommit_max.sh", "image.png"]
        self.root = _root()

    def _safe_rmtree(self, path: Path) -> bool:
        if not path.exists():
            return False
        try:
            shutil.rmtree(path)
            return True
        except OSError as e:
            print(f"⚠️  No se pudo eliminar {path}: {e}", file=sys.stderr)
            return False

    def _remove_pycache_under_root(self) -> int:
        """Borra carpetas __pycache__ bajo el repo; no entra en .git / .venv / node_modules."""
        found: list[Path] = []
        skip_top = {".git", ".venv", "venv", "node_modules", "dist", "build"}
        for dirpath, dirnames, _filenames in os.walk(self.root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in skip_top]
            if Path(dirpath).name == "__pycache__":
                found.append(Path(dirpath))
        n = 0
        for p in sorted(found, key=lambda x: len(x.parts), reverse=True):
            try:
                rel = p.relative_to(self.root)
            except ValueError:
                continue
            if self._safe_rmtree(p):
                print(f"🗑️ Eliminado: {rel}")
                n += 1
        return n

    def ejecutar_limpieza(self) -> str:
        print("🧹 Iniciando limpieza de residuos bajo el repo…")

        print(f"✅ [Jules]: Sello operativo alineado con @CertezaAbsoluta / rama de trabajo.")
        print(f"    ROOT: {self.root}")

        trash_paths = [
            self.root / ".next",
            self.root / "node_modules" / ".cache",
            self.root / "mirror_ui" / "node_modules" / ".cache",
            self.root / "temp_logs",
        ]
        for folder in trash_paths:
            if self._safe_rmtree(folder):
                print(f"🗑️ Eliminado: {folder.relative_to(self.root)}")

        self._remove_pycache_under_root()

        print(f"💎 Referencia activos: SIRET {self.siret} · patente {self.patent}")
        print(f"📌 Archivos críticos (no se borran; solo referencia): {', '.join(self.critical_files)}")

        return "✨ Búnker limpio. JULES enfocado 100% en la liquidez de Bpifrance."


if __name__ == "__main__":
    jules = BunkerCleaner()
    print(jules.ejecutar_limpieza())
