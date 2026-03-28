#!/usr/bin/env python3
"""Checks: backend, mirror_ui, .venv imports, node/npm. Exit 1 on failure."""
from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    print(f"[verify_system] ROOT={root}")
    err = 0
    checks = [
        (root / "backend" / "requirements.txt", "backend/requirements.txt"),
        (root / "mirror_ui" / "package.json", "mirror_ui/package.json"),
        (root / "backend" / "omega_core.py", "backend/omega_core.py"),
    ]
    for p, label in checks:
        if p.is_file():
            print(f"  OK  {label}")
        else:
            print(f"  FAIL  falta {label}")
            err += 1
    py = root / ".venv" / "bin" / "python3"
    if not py.is_file():
        py = root / ".venv" / "bin" / "python"
    if py.is_file():
        r = subprocess.run(
            [str(py), "-c", "import fastapi, uvicorn, pydantic"],
            cwd=str(root),
            capture_output=True,
        )
        if r.returncode == 0:
            print("  OK  .venv backend imports")
        else:
            print("  FAIL  .venv imports")
            err += 1
    else:
        print("  FAIL  no .venv")
        err += 1
    for cmd in ("node", "npm"):
        r = subprocess.run([cmd, "--version"], capture_output=True, text=True)
        if r.returncode == 0:
            v = (r.stdout or r.stderr).strip().splitlines()[0]
            print(f"  OK  {cmd}: {v}")
        else:
            print(f"  FAIL  {cmd}")
            err += 1
    if err:
        print(f"\n[verify_system] {err} problema(s).")
        return 1
    print("\n[verify_system] OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
