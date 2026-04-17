"""
Mirror Sanctuary V10 — orquestación ligera (activos visuales + comprobación Stripe).

Claves Stripe (en entorno, nunca en el código):
  STRIPE_SECRET_KEY_FR primero; luego STRIPE_SECRET_KEY, E50_* o STRIPE_API_KEY (compat).

Raíz del proyecto: E50_PROJECT_ROOT o ~/tryonyou-app

python3 mirror_sanctuary_v10.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

PATENTE = "PCT/EP2025/067317"

# Rutas relativas a ROOT donde suelen vivir vídeo / overlays (ajusta con E50_MEDIA_DIRS).
DEFAULT_MEDIA_SUBDIRS = ("public", "static", "src/assets", "assets", "media")


def _project_root() -> Path:
    return Path(
        os.environ.get(
            "E50_PROJECT_ROOT",
            os.path.expanduser("~/tryonyou-app"),
        )
    ).resolve()


def _stripe_secret() -> str:
    return (
        os.environ.get("STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("INJECT_STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("E50_STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY", "").strip()
        or os.environ.get("E50_STRIPE_SECRET_KEY", "").strip()
        or os.environ.get("STRIPE_API_KEY", "").strip()
    )


def _media_extensions() -> tuple[str, ...]:
    raw = os.environ.get("E50_MEDIA_EXTENSIONS", "").strip()
    if raw:
        return tuple(x.strip().lower() for x in raw.split(",") if x.strip())
    return (".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp", ".svg")


class MirrorSanctuaryV10:
    def __init__(self) -> None:
        self.root = _project_root()
        self.precision = 98.4
        self.brand = "Balmain"
        # CONSOLIDA 70 cierra build/entrega; Jules (log/criterio); Team50 activos.
        # Mesas de listings (soberanía, inversión) alineadas con omega_consolidator_safe.
        self.active_agents = ["Jules", "Agent70", "Team50"]

    def check_visual_assets(self) -> dict[str, object]:
        """Comprueba que existan directorios de medios y enumera archivos conocidos."""
        print("🛡️ [TEAM 50] Verificando integridad de video y capas...")
        extra = os.environ.get("E50_MEDIA_DIRS", "").strip()
        subdirs = list(DEFAULT_MEDIA_SUBDIRS)
        if extra:
            subdirs.extend(p.strip() for p in extra.split(",") if p.strip())

        exts = _media_extensions()
        found: list[str] = []
        checked_dirs: list[str] = []

        for rel in subdirs:
            base = self.root / rel
            checked_dirs.append(str(base))
            if not base.is_dir():
                continue
            for path in base.rglob("*"):
                if path.is_file() and path.suffix.lower() in exts:
                    try:
                        found.append(str(path.relative_to(self.root)))
                    except ValueError:
                        found.append(str(path))

        status = "ok" if found else ("warn" if any(Path(d).is_dir() for d in checked_dirs) else "empty")
        report = {
            "status": status,
            "root": str(self.root),
            "scanned_subdirs": subdirs,
            "files_found": len(found),
            "sample": found[:15],
        }
        print(f"   → {report['files_found']} activo(s) bajo {len(subdirs)} ruta(s) relativa(s).")
        if found:
            for p in report["sample"][:5]:
                print(f"      · {p}")
            if len(found) > 5:
                print(f"      · … (+{len(found) - 5} más)")
        else:
            print("   → Sin archivos de medios aún; añade vídeo/PNG en public/ o define E50_MEDIA_DIRS.")
        return report

    def execute_snap(self, look_id: str) -> None:
        """Registro del look activo (sin side-effects críticos)."""
        print(f"⚡ [AGENT 70] Activando look {look_id!r} con overlay {self.brand}...")
        log_dir = self.root / "src" / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "mirror_sanctuary_snap_log.json"
        payload = {
            "look_id": look_id,
            "brand": self.brand,
            "ts": datetime.now(timezone.utc).isoformat(),
            "patente": PATENTE,
        }
        import json

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"   → Registro: {log_path.relative_to(self.root)}")

    def generate_revenue(self) -> str:
        """Comprueba la clave Stripe (Balance) sin crear cargos ni productos."""
        key = _stripe_secret()
        if not key:
            return "❌ Error: falta clave (STRIPE_SECRET_KEY, E50_STRIPE_SECRET_KEY o STRIPE_API_KEY)."

        import stripe

        stripe.api_key = key
        print("💰 [JULES] Comprobando conexión Stripe (solo lectura /balance)...")
        try:
            stripe.Balance.retrieve()
            return "✅ Stripe: clave válida (balance consultado)."
        except Exception as e:
            return f"❌ Stripe: {e}"


if __name__ == "__main__":
    bunker = MirrorSanctuaryV10()
    print(f"🏛️ Mirror Sanctuary V10 — patente {PATENTE}")
    print(f"   ROOT: {bunker.root}")
    bunker.check_visual_assets()
    bunker.execute_snap(os.environ.get("E50_LOOK_ID", "balmain_default"))
    print(bunker.generate_revenue())
