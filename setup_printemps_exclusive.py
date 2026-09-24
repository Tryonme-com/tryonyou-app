"""
Nodo de exclusividad Printemps (75009): manifiesto satélite + fragmento de bienvenida.

- Escribe `exclusivity_75009.json`.
- Fusiona en `production_manifest.json` la clave `printemps_exclusive` (no borra lockdown ni deployment).
- Guarda el mensaje de bienvenida en `partners/printemps_welcome_fragment.html` (listo para integrar en UI).
- Git: add + commit + **push normal** (sin --force). `TRYONYOU_SKIP_GIT=1` para solo archivos.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "production_manifest.json"
EXCLUSIVE_JSON = ROOT / "exclusivity_75009.json"
PARTNERS_DIR = ROOT / "partners"
WELCOME_FRAG = PARTNERS_DIR / "printemps_welcome_fragment.html"

COMMIT_MSG = (
    "STRATEGY: exclusividad 75009 Printemps (VIP); nodo Lafayette en conflicto operativo. "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

WELCOME_HTML = """
<div id="partner-welcome" style="background:#000;color:#D4AF37;padding:50px;text-align:center;font-family:serif,Georgia,serif;">
    <h1 style="letter-spacing:5px;">BIENVENUE PRINTEMPS</h1>
    <p style="color:#eee;">Technologie Biométrique Zero-Size | Exclusivité Code Postal 75009 activée.</p>
    <p style="font-size:0.8rem;opacity:0.5;">Sous la protection du Brevet PCT/EP2025/067317</p>
</div>
"""


def _git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def setup_printemps() -> int:
    print("\n--- 🔱 NODAL EXCLUSIVITY: PRINTEMPS 75009 ---")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest_satellite = {
        "node": "PRINTEMPS-75009",
        "status": "VIP_PREMIUM",
        "license_type": "ZIP_CODE_EXCLUSIVE",
        "rate": 16200,
        "protection": "GOOGLE_STUDIO_SOVEREIGNTY",
        "sealed_at_utc": ts,
        "patent": "PCT/EP2025/067317",
        "siret": "94361019600017",
    }
    EXCLUSIVE_JSON.write_text(
        json.dumps(manifest_satellite, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"✅ {EXCLUSIVE_JSON.name} sellado.")

    PARTNERS_DIR.mkdir(parents=True, exist_ok=True)
    WELCOME_FRAG.write_text(WELCOME_HTML.strip() + "\n", encoding="utf-8")
    print(f"✅ Bienvenida: {WELCOME_FRAG.relative_to(ROOT)}")

    if MANIFEST.is_file():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        data["printemps_exclusive"] = {
            **manifest_satellite,
            "welcome_fragment": str(WELCOME_FRAG.relative_to(ROOT)),
        }
        data.setdefault("node_routing_note", {})
        if isinstance(data["node_routing_note"], dict):
            data["node_routing_note"].update(
                {
                    "PRINTEMPS-75009": "VIP_PREMIUM_WELCOME",
                    "LAFAYETTE_75009": "CONFLICT_STATUS",
                    "updated_utc": ts,
                }
            )
        MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("✅ production_manifest.json — clave printemps_exclusive fusionada.")

    print("✅ Nodo Printemps listo. Integra el fragmento en la UI según hostname (p. ej. printemps).")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("ℹ️  TRYONYOU_SKIP_GIT=1 — sin commit/push.")
        return 0

    _git(["add", "."])
    rc = _git(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Commit omitido o sin cambios.", file=sys.stderr)
    rc = _git(["push", "origin", "main"])
    if rc != 0:
        print("⚠️  git push falló.", file=sys.stderr)
        return rc

    print("\n--- 🔱 Exclusividad sincronizada en main ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(setup_printemps())
