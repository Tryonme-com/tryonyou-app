"""
Escribe src/data/divineo_history.json. Limpieza de carpetas solo con E50_PURGE_DIVINEO=1.

Sin ese flag, solo lista rutas que existirían bajo ROOT (no borra nada).

Rutas candidatas (relativas a ROOT): src/tests, logs, tmp, old_versions

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 destilar_divineo_total_safe.py
          E50_PURGE_DIVINEO=1 python3 destilar_divineo_total_safe.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

RUTAS_LIMPIAR = [
    "src/tests",
    "logs",
    "tmp",
    "old_versions",
]


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _safe_under_root(path: str) -> bool:
    root_real = os.path.realpath(ROOT)
    target = os.path.realpath(path)
    return target == root_real or target.startswith(root_real + os.sep)


def destilar_divineo_total_safe() -> int:
    print("✨ Destilación Divineo (registro JSON + limpieza opcional)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    legado = {
        "_note": "Document narratif / produit. Pas une preuve légale ni un audit.",
        "origen": "Nacimiento de TryOnYou France",
        "hitos_consolidados": [
            "Integración de Motor Biométrico 99.7%",
            "Protocolo de Pago ABVET (Iris + Voz)",
            "Arquitectura de Lujo V10 Omega",
            "Portal VIP Friends & SACMuseum",
            "Estrategia de Asalto a Station F y Bpifrance",
            "Patente Blindada PCT/EP2025/067317",
        ],
        "filosofia": "Yo no sé de marcas ni de números, pero yo sé que estoy bien divina.",
        "estado_actual": "CONFIG_LOCAL_NARRATIVE",
        "ultima_actualizacion": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    out_rel = os.path.join("src", "data", "divineo_history.json")
    out_path = os.path.join(ROOT, out_rel)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(legado, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ {out_rel}")

    for rel in RUTAS_LIMPIAR:
        ruta = os.path.join(ROOT, rel)
        if not os.path.exists(ruta):
            continue
        if not _safe_under_root(ruta):
            print(f"⚠️  Omitido (fuera de ROOT): {rel}")
            continue
        if _on("E50_PURGE_DIVINEO"):
            try:
                shutil.rmtree(ruta)
                print(f"🧹 Eliminado: {rel}")
            except OSError as e:
                print(f"❌ No se pudo borrar {rel}: {e}")
        else:
            print(f"ℹ️  Existe (no borrado; usa E50_PURGE_DIVINEO=1): {rel}")

    print("\n" + "—" * 60)
    print("Registro divineo_history.json actualizado.")
    if not _on("E50_PURGE_DIVINEO"):
        print("Ninguna carpeta eliminada sin E50_PURGE_DIVINEO=1.")
    print("—" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(destilar_divineo_total_safe())
