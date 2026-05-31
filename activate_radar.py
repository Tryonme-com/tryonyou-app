"""Escribe radar_config.json bajo el proyecto. python3 activate_radar.py"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)


def activate_radar() -> int:
    print("🛡️ Paso 3: Activando Radar de Litigio...")
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)
    radar_config = {
        "active": True,
        "target_region": "Paris",
        "target_sectors": ["Luxe", "Banking"],
        "monitoring_agents": ["Jules", "70"],
        "status": "OPERATIONAL",
    }
    rel = os.path.join("src", "data", "radar_config.json")
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(radar_config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ Radar de París conectado. → {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(activate_radar())
