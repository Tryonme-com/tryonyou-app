import os
import json
import datetime
import subprocess

import requests

# === CONFIGURACIÓN SOBERANA (75001) ===
CONFIG = {
    "total_due": "16.200 € TTC",
    "project": "tryonyou-app",
}

GIT_COMMIT_SUFFIX = (
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 | "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)


def _repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _make_webhook_url() -> str:
    return (
        (os.getenv("MAKE_WEBHOOK_URL") or "").strip()
        or (os.getenv("MAKE_WEBHOOK_TRIGGER_50_AGENTS") or "").strip()
    )


def clean_orphans() -> None:
    """Elimina scripts antiguos para evitar ruido en el búnker."""
    root = _repo_root()
    orphans = ["terminal_cleanup.py", "check_system_health.py", "deploy_omega_final.py"]
    for name in orphans:
        path = os.path.join(root, name)
        if os.path.isfile(path):
            os.remove(path)
            print(f"🔥 Eliminado archivo huérfano: {name}")


def run_omega_cycle() -> None:
    """Ejecuta el ciclo de 50 agentes y sella Git."""
    print(f"🚀 [{datetime.datetime.now().strftime('%H:%M:%S')}] Iniciando Ciclo Omega...")

    clean_orphans()

    url = _make_webhook_url()
    if not url:
        print("⚠️ Nube: Defina MAKE_WEBHOOK_URL o MAKE_WEBHOOK_TRIGGER_50_AGENTS.")
    else:
        try:
            res = requests.post(url, json={"action": "run_full_cycle"}, timeout=120)
            print(f"📡 Nube: Status {res.status_code}")
        except Exception as e:
            print(f"⚠️ Error Nube: {e}")

    root = _repo_root()
    lock_path = os.path.join(root, "node_lock_status.json")
    with open(lock_path, "w") as f:
        json.dump(
            {
                "node": "75009",
                "restriction": "LOCKED",
                "total_due": CONFIG["total_due"],
                "debt_eur": 16200.0,
            },
            f,
            indent=4,
        )

    base_msg = (
        f"🔒 Omega Auto-Pilot: Ciclo completado. Nodo 75009 bloqueado ({CONFIG['total_due']})"
    )
    commit_msg = f"{base_msg} | {GIT_COMMIT_SUFFIX}"
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=root)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=root)
        print(f"✅ Git: {base_msg}")
    except subprocess.CalledProcessError:
        print("✅ Git: Sin cambios adicionales.")


if __name__ == "__main__":
    run_omega_cycle()
    print("\n🔱 SISTEMA SELLADO POR 2 HORAS. VÍVELO. 💥")
