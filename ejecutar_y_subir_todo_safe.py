"""
Push acotado (sin git add .). Lista de rutas «bundle»; solo se añaden las que existan.

- E50_GIT_PUSH=1 obligatorio.
- E50_FORCE_PUSH=1 para --force.
- E50_DEPLOY_PATHS='a,b,c' sustituye la lista completa.

Raíz: E50_PROJECT_ROOT (cwd de git).

python3 ejecutar_y_subir_todo_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

DEFAULT_BUNDLE = [
    "src/data/genesis_manifest.json",
    "src/data/divineo_history.json",
    "src/data/system_manifest.json",
    "src/data/mesa_listos_audit.json",
    "src/data/vip_access_list.json",
    "src/data/bunker_radar_sync.json",
    "src/data/omega_seal.json",
    "src/seo/linkedin_og_fragment.html",
    "src/seo/authority_social_metadata.html",
    "src/constants/stripe_links.ts",
    "src/components/SubscriptionPanel.tsx",
    "src/components/StripePayButton.tsx",
    "src/config/payment_settings.ts",
    "src/components/special/StationFWelcome.tsx",
    "src/modules/legal/bpifranceReport.ts",
    "vercel.json",
]


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _run(argv: list[str], *, cwd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def ejecutar_y_subir_todo_safe() -> int:
    print("🚀 Despliegue OMEGA (git acotado, sin add .)...")

    os.makedirs(ROOT, exist_ok=True)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Define E50_GIT_PUSH=1 para ejecutar git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    raw = os.environ.get("E50_DEPLOY_PATHS", "").strip()
    if raw:
        paths = [p.strip() for p in raw.split(",") if p.strip()]
    else:
        paths = list(DEFAULT_BUNDLE)

    exist = [p for p in paths if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Ninguna ruta del bundle existe. Ajusta E50_DEPLOY_PATHS o genera archivos.")
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    msg = (
        os.environ.get("E50_COMMIT_MSG", "").strip()
        or f"DEPLOY OMEGA: {ts} - TryOnYou France Live"
    )

    r = _run(["git", "add", *exist], cwd=ROOT)
    if r.returncode != 0:
        print("❌ git add falló:", r.stderr)
        return 1
    print("✅ git add:", len(exist), "rutas")

    # Mejor que parsear stderr: ¿hay diff índice vs HEAD?
    has_head = _run(["git", "rev-parse", "-q", "--verify", "HEAD"], cwd=ROOT).returncode == 0
    if has_head:
        staged = _run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if staged.returncode == 0:
            print(
                "ℹ️  Nada nuevo que commitear en el bundle (índice = HEAD). "
                "Se intenta push por si hay commits locales sin subir."
            )
        else:
            r = _run(["git", "commit", "-m", msg], cwd=ROOT)
            if r.returncode != 0:
                out = ((r.stdout or "") + (r.stderr or "")).lower()
                benign = any(
                    s in out
                    for s in (
                        "nothing to commit",
                        "nothing added to commit",
                        "no changes added to commit",
                        "working tree clean",
                    )
                )
                if benign:
                    print("ℹ️  git commit sin efecto (mensaje benigno). Siguiente: push.")
                else:
                    print("❌ git commit:", r.stderr or r.stdout)
                    return 1
    else:
        r = _run(["git", "commit", "-m", msg], cwd=ROOT)
        if r.returncode != 0:
            print("❌ git commit (sin HEAD previo):", r.stderr or r.stdout)
            return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    r = _run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print("❌ git push falló:", r.stderr)
        print("💡 Revisa auth (token SSH/HTTPS) en este entorno.")
        return 1

    print("\n" + "=" * 60)
    print("Push enviado al remoto (revisa GitHub y el hook de Vercel).")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(ejecutar_y_subir_todo_safe())
