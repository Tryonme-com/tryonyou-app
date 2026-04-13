"""
Fit-AI Assistant — cruce escaneo biométrico ↔ catálogo Live It (Google Drive).

Validación de entorno (sin secretos en logs). Implementación Drive: ampliar con
google-api-python-client cuando el servicio esté acreditado.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
from typing import Any


def fit_ai_assistant_health() -> dict[str, Any]:
    """Comprueba variables necesarias para cruce Fit-AI + Live It Drive."""
    folder = (os.environ.get("LIVEIT_DRIVE_COLLECTION_FOLDER_ID") or "").strip()
    sa = (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    sync = (os.environ.get("FIT_AI_LIVEIT_SYNC_ENABLED") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    ok_folder = len(folder) >= 8
    ok_sa = bool(sa) and os.path.isfile(sa)
    ready = ok_folder and (ok_sa or not sync)
    return {
        "status": "ok" if ready else "degraded",
        "liveit_drive_folder_configured": ok_folder,
        "service_account_path_set": bool(sa),
        "service_account_file_exists": ok_sa,
        "fit_ai_liveit_sync_enabled": sync,
        # Cierre soberano: Agente 70 valida entorno Fit-AI hasta entrega (Make/webhooks pueden leer el flag).
        "decision_final_por": "AGENTE70",
        "cierre_operativo_hasta_entrega": True,
        "hint": "Define LIVEIT_DRIVE_COLLECTION_FOLDER_ID y GOOGLE_APPLICATION_CREDENTIALS "
        "(JSON cuenta de servicio con acceso a la carpeta Live It). "
        "FIT_AI_LIVEIT_SYNC_ENABLED=0 permite modo solo lectura de env sin SA.",
    }
