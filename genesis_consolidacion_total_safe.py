"""
Crea árbol src/*, escribe src/data/genesis_manifest.json, comprueba variables de entorno.
Git opcional y acotado (manifiesto + .gitkeep en carpetas nuevas), sin git add . ni --force por defecto.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1, E50_FORCE_PUSH=1 opcional.
- E50_STRICT=1 — exit 1 si falta alguna clave requerida en el entorno.

Ejecutar: python3 genesis_consolidacion_total_safe.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

FOLDERS = [
    "src/components/biometrics",
    "src/components/commerce",
    "src/components/marketing",
    "src/modules/legal",
    "src/data",
    "src/agents",
]

REQUIRED_KEYS = [
    "GOOGLE_API_KEY",
    "EMAIL_USER",
    "EMAIL_PASS",
    "STRIPE_SECRET_KEY",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _key_ok(name: str) -> bool:
    if os.environ.get(name, "").strip():
        return True
    if name == "GOOGLE_API_KEY" and os.environ.get("GOOGLE_AI_API_KEY", "").strip():
        return True
    if name == "STRIPE_SECRET_KEY":
        return bool(
            os.environ.get("INJECT_STRIPE_SECRET_KEY", "").strip()
            or os.environ.get("E50_STRIPE_SECRET_KEY", "").strip()
        )
    if name == "EMAIL_USER":
        return bool(os.environ.get("E50_SMTP_USER", "").strip())
    if name == "EMAIL_PASS":
        return bool(os.environ.get("E50_SMTP_PASS", "").strip())
    return False


def genesis_consolidacion_total_safe() -> int:
    print("💎 GÉNESIS V10 (estructura + manifiesto + comprobación env)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    gitkeep_paths: list[str] = []
    for rel in FOLDERS:
        path = os.path.join(ROOT, rel)
        created = not os.path.isdir(path)
        os.makedirs(path, exist_ok=True)
        if created:
            gk = os.path.join(path, ".gitkeep")
            if not os.path.isfile(gk):
                with open(gk, "w", encoding="utf-8") as gf:
                    gf.write("")
                gitkeep_paths.append(os.path.join(rel, ".gitkeep"))
            print(f"✅ Carpeta creada: {rel}")

    adn = {
        "_note": "Manifeste descriptif local. Vérifier brevet et montants avant usage officiel.",
        "project": "TryOnYou France",
        "architect": "Rubén Espinar Rodríguez",
        "patent_id": "PCT/EP2025/067317",
        "tech_stack": {
            "orchestrator": "P.A.U. V10 Omega",
            "ai_engine": "Gemini 2.0 Flash (Studio Config 0.1 Temp)",
            "payment": "ABVET Biometric Gateway",
            "hosting": "Vercel / Deep Tech Edge",
        },
        "business_logic": {
            "maintenance_fee": "100 EUR",
            "license_enterprise": "141,986 EUR",
            "target": "Station F / LVMH / Bpifrance",
        },
        "consolidated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    manifest_rel = os.path.join("src", "data", "genesis_manifest.json")
    manifest_path = os.path.join(ROOT, manifest_rel)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(adn, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ {manifest_rel}")

    print("\n🔐 Comprobación de variables (solo presencia, sin valores):")
    missing = [k for k in REQUIRED_KEYS if not _key_ok(k)]
    for k in REQUIRED_KEYS:
        print(f"   {k}: {'ok' if _key_ok(k) else 'falta'}")
    if missing:
        print(f"⚠️  Faltan: {', '.join(missing)}")

    if missing and _on("E50_STRICT"):
        print("❌ E50_STRICT=1 y faltan claves en el entorno.")
        return 1

    if not _on("E50_GIT_PUSH"):
        print("\nℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    to_add = [manifest_rel, *gitkeep_paths]
    exist = [p for p in to_add if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    msg = (
        f"GENESIS_CONSOLIDATION_V10: Full system lock at "
        f"{datetime.now(timezone.utc).strftime('%H:%M')}Z"
    )
    rc = _run(["git", "commit", "-m", msg], cwd=ROOT)
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado (rutas explícitas, sin add .).")
    return 0


if __name__ == "__main__":
    sys.exit(genesis_consolidacion_total_safe())
