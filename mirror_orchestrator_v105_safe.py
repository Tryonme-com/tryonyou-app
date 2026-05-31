"""Mirror Orchestrator V10.5 — delega en protocolo Soberanía Total (PCT/EP2025/067317)."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

def main() -> None:
    root = Path(__file__).resolve().parent
    script = root / "protocolo_soberania_total.py"
    if script.is_file():
        sys.argv = [str(script)]
        runpy.run_path(str(script), run_name="__main__")
    else:
        print("Falta protocolo_soberania_total.py en la raíz del repo.")

if __name__ == "__main__":
    main()
