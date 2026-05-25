from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

REQUIRED_ENV_VARS = (
    "PENNYLANE_API_KEY",
    "SPREADSHEET_ID",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _result(name: str, status: str, detail: str, started_at: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "started_at": started_at,
        "finished_at": _utc_now(),
    }


def run_balance_sync() -> dict[str, Any]:
    started_at = _utc_now()
    missing_env = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name, "").strip()]
    if missing_env:
        return _result(
            "balance_soberana",
            "skipped",
            f"Integración financiera omitida; faltan variables: {', '.join(missing_env)}",
            started_at,
        )

    try:
        from scripts.pennylane_google_sheets_sync import main_execution
    except ModuleNotFoundError as exc:
        missing_dependency = exc.name or "desconocida"
        return _result(
            "balance_soberana",
            "error",
            f"No se pudo importar la sincronización financiera; falta la dependencia: {missing_dependency}",
            started_at,
        )
    except Exception as exc:
        return _result(
            "balance_soberana",
            "error",
            f"No se pudo preparar la sincronización financiera: {exc}",
            started_at,
        )

    exit_code = int(main_execution())
    if exit_code == 0:
        return _result(
            "balance_soberana",
            "success",
            "Sincronización financiera completada correctamente.",
            started_at,
        )

    return _result(
        "balance_soberana",
        "error",
        f"La sincronización financiera terminó con código {exit_code}.",
        started_at,
    )
