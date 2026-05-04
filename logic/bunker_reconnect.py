"""
Módulo de Reconexión — Búnker V10.2 ↔ Make.com

Resuelve errores de tipo CONCURRENT_UPDATES / SCENARIO_FAIL limpiando los
bloqueos de concurrencia en el escenario de Make.com y restableciendo la
integración OpenAI/ChatGPT Tools.

Patente PCT/EP2025/067317 — @CertezaAbsoluta
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Callable, Final

_DEFAULT_TARGET: Final[str] = "Integration_OpenAI_ChatGPT_Tools"
_DEFAULT_ACTION: Final[str] = "clear_concurrent_locks"
_STATUS_RESET: Final[str] = "RESETTING_CONCURRENCY"
_STATUS_PENDING_WEBHOOK: Final[str] = "PENDING_MAKE_WEBHOOK"
_STATUS_OK: Final[str] = "RECONNECTED"
_STATUS_FAILED: Final[str] = "MAKE_RECONNECT_FAILED"
SUCCESS_MESSAGE: Final[str] = "A FUEGO: BunkerControl reconectado con Make.com."
SKIPPED_MESSAGE: Final[str] = "BunkerControl preparado; falta webhook Make.com en entorno."
FAILURE_MESSAGE: Final[str] = "BunkerControl no pudo reconectar Make.com."

_WEBHOOK_ENV_KEYS: Final[tuple[str, ...]] = (
    "MAKE_BUNKER_RECONNECT_WEBHOOK_URL",
    "MAKE_BUNKER_CONTROL_WEBHOOK_URL",
    "MAKE_WEBHOOK_URL",
)
_DEFAULT_TIMEOUT_SECONDS: Final[int] = 25

_PostFunc = Callable[[str, dict[str, Any], int], Any]


class BunkerControl:
    """Controla la reconexión del Búnker V10.2 con Make.com."""

    def __init__(
        self,
        *,
        session: str | None = None,
        target: str = _DEFAULT_TARGET,
        webhook_url: str | None = None,
        post: _PostFunc | None = None,
        timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.session: str = session or os.getenv("BUNKER_SESSION_TOKEN", "")
        self.target = target
        self.webhook_url = webhook_url if webhook_url is not None else resolve_make_webhook_url()
        self._post = post or _post_json
        self.timeout_seconds = timeout_seconds
        self.status = _STATUS_RESET
        self.last_payload: dict[str, Any] | None = None
        self.last_response_code: int | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fix_sync(self) -> str:
        """Limpia bloqueos de concurrencia y reconecta el búnker con Make.com.

        Returns:
            Mensaje de confirmación al completar el restablecimiento.
        """
        print(f"--- [FORCE RESET: {_session_label(self.session)}] ---")

        sync_payload = self._build_payload()
        self.last_payload = sync_payload
        print(f"SINCRO: limpiando errores Make.com (target={sync_payload['target']})")

        if not self.webhook_url:
            self.status = _STATUS_PENDING_WEBHOOK
            print("ESTADO: webhook Make.com no configurado; payload preparado.")
            return SKIPPED_MESSAGE

        try:
            response = self._post(self.webhook_url, sync_payload, self.timeout_seconds)
        except Exception as exc:  # pragma: no cover - exact exception type depends on the HTTP client.
            self.status = _STATUS_FAILED
            print(f"ERROR: Make.com no disponible: {exc}", file=sys.stderr)
            return FAILURE_MESSAGE

        self.last_response_code = int(getattr(response, "status_code", 0) or 0)
        if not _response_ok(response):
            self.status = _STATUS_FAILED
            response_text = str(getattr(response, "text", ""))[:300]
            print(
                f"ERROR: Make.com devolvio HTTP {self.last_response_code}: {response_text}",
                file=sys.stderr,
            )
            return FAILURE_MESSAGE

        print("ESTADO: Bunker TryOnYou reconectado con Make.com.")
        self.status = _STATUS_OK
        return SUCCESS_MESSAGE

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_payload(self) -> dict[str, Any]:
        return {
            "event": "bunker_control_reconnect",
            "source": "tryonyou_bunker_control",
            "target": self.target,
            "action": _DEFAULT_ACTION,
            "status": _STATUS_RESET,
            "error_codes": ["CONCURRENT_UPDATES", "SCENARIO_FAIL"],
            "location": "oberkampf_75011",
            "protocol": "V10.2",
            "patent": "PCT/EP2025/067317",
            "session_present": bool(self.session),
            "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pau_override": True,
        }


def resolve_make_webhook_url() -> str:
    """Devuelve el primer webhook Make.com configurado, sin valores por defecto ficticios."""
    for key in _WEBHOOK_ENV_KEYS:
        value = (os.getenv(key) or "").strip()
        if value:
            return value
    return ""


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: int) -> Any:
    import requests

    return requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=timeout_seconds,
    )


def _response_ok(response: Any) -> bool:
    ok = getattr(response, "ok", None)
    if ok is not None:
        return bool(ok)
    status_code = int(getattr(response, "status_code", 0) or 0)
    return 200 <= status_code < 300


def _session_label(session: str) -> str:
    if not session:
        return "N/A"
    return f"REDACTED(len={len(session)})"


def main() -> int:
    control = BunkerControl()
    result = control.fix_sync()
    print(result)
    return 1 if control.status == _STATUS_FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
