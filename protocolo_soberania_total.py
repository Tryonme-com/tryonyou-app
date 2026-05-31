"""Protocolo Soberanía Total — PCT/EP2025/067317. python3 protocolo_soberania_total.py"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PATENTE = "PCT/EP2025/067317"
TARGET_SANTUARIO = 121


def _root() -> Path:
    return Path(os.environ.get("E50_PROJECT_ROOT", os.getcwd())).resolve()


def purga_cache(root: Path) -> None:
    print("🧹 Purga caché / build...")
    names = ("node_modules", "dist", ".vite", ".next", "build", "package-lock.json")
    for base in (root, root / "mirror_ui"):
        for name in names:
            p = base / name
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            elif p.is_file():
                try:
                    p.unlink()
                except OSError:
                    pass
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        if Path(dirpath).name == "__pycache__":
            shutil.rmtree(dirpath, ignore_errors=True)
            dirnames.clear()


def _collect_santuario_files(root: Path) -> list[str]:
    rels: list[str] = []
    for sr in (root / "mirror_ui", root / "backend", root / "api", root / "src"):
        if sr.is_dir():
            for p in sr.rglob("*"):
                if p.is_file():
                    rels.append(str(p.relative_to(root)).replace("\\", "/"))
    for p in root.glob("*.py"):
        rels.append(p.name)
    for name in ("index.html", "vercel.json", "requirements.txt"):
        if (root / name).is_file():
            rels.append(name)
    for p in root.rglob("*.py"):
        if ".git" in p.parts:
            continue
        rels.append(str(p.relative_to(root)).replace("\\", "/"))
    return sorted(set(rels))


def consolidar_santuario(root: Path) -> None:
    archivos = _collect_santuario_files(root)
    dd = root / "src" / "data"
    dd.mkdir(parents=True, exist_ok=True)
    out = dd / "mirror_sanctuary_v10_consolidacion.json"
    out.write_text(
        json.dumps(
            {
                "patente": PATENTE,
                "protocolo": "SOBERANIA_TOTAL_V10",
                "ts_utc": datetime.now(timezone.utc).isoformat(),
                "archivos_totales": len(archivos),
                "objetivo_corpus": TARGET_SANTUARIO,
                "archivos": archivos,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"📦 {len(archivos)} rutas → {out.relative_to(root)}")


def _run(cmd: list[str], cwd: Path) -> None:
    print(f"▶ {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=str(cwd), timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"⚠️ ignorado: {e}")


def main() -> int:
    root = _root()
    os.chdir(root)
    print(f"🏛️ Soberanía Total — {PATENTE}")
    purga_cache(root)
    consolidar_santuario(root)
    _run([sys.executable, str(root / "mirror_sanctuary_v10.py")], root)
    _run([sys.executable, str(root / "omega_consolidator_safe.py")], root)
    _run(["npx", "--yes", "vercel", "deploy", "--prod", "--yes"], root)
    print("✅ Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
