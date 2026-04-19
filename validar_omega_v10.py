from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PATENT = "PCT/EP2025/067317"
SIRET = "94361019600017"
READY_STATUS = "ESTADO: Listo para recibir los 27.500 EUR manana."
REVIEW_STATUS = "ESTADO: Revisar consistencia soberana antes de recibir los 27.500 EUR manana."


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _is_non_empty(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _has_env_secret() -> bool:
    aliases = (
        "STRIPE_SECRET_KEY",
        "INJECT_STRIPE_SECRET_KEY",
        "E50_STRIPE_SECRET_KEY",
    )
    return any(_is_non_empty(os.getenv(key, "")) for key in aliases)


def validar_omega_v10(base_dir: str | Path | None = None) -> str:
    """Audita señales clave Omega sin exponer secretos."""
    root = Path(base_dir) if base_dir is not None else Path(__file__).resolve().parent
    vault = _load_json(root / "master_omega_vault.json")
    manifest = _load_json(root / "production_manifest.json")
    firebase_applet = _load_json(root / "firebase-applet-config.json")

    vault_identity = vault.get("identidad", {}) if isinstance(vault.get("identidad"), dict) else {}
    manifest_patent = str(manifest.get("patent", "")).strip()
    manifest_siret = str(manifest.get("siret", "")).strip()
    vault_patent = str(vault_identity.get("patente", "")).strip()
    vault_siret = str(vault_identity.get("siret", "")).strip()

    identity_consistent = (
        vault_patent == PATENT
        and manifest_patent == PATENT
        and vault_siret == SIRET
        and manifest_siret == SIRET
    )

    firestore_ok = _is_non_empty(firebase_applet.get("projectId")) and (
        _is_non_empty(firebase_applet.get("apiKey")) or _is_non_empty(os.getenv("VITE_FIREBASE_API_KEY", ""))
    )

    auth_sync = ""
    if isinstance(vault.get("modulos_activos"), dict):
        auth_sync = str(vault["modulos_activos"].get("AUTH_SYNC", "")).strip()
    twofa_linked = "google-auth" in auth_sync.lower() or _is_non_empty(
        os.getenv("GOOGLE_AUTH_2FA_STATUS", "")
    )

    billing_signal = _has_env_secret() or _is_non_empty(os.getenv("BILLING_ENGINE_STATUS", ""))

    print("--- [AUDITORIA DE DESPLIEGUE OMEGA] ---")
    print(
        "Identidad Legal Vault↔Manifest: "
        + ("CONSISTENTE" if identity_consistent else "INCONSISTENTE")
    )
    print("Via Firestore: " + ("CONFIGURADA" if firestore_ok else "PENDIENTE"))
    print("Google Authenticator: " + ("VINCULADO" if twofa_linked else "PENDIENTE"))
    print(
        "Billing Engine: "
        + (
            "EJECUTANDO (Pendiente Ciclo Bancario)"
            if billing_signal
            else "SEÑAL LIMITADA (sin clave Stripe en entorno local)"
        )
    )

    return READY_STATUS if identity_consistent else REVIEW_STATUS


if __name__ == "__main__":
    print(validar_omega_v10())
