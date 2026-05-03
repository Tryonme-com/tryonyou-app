"""
FinancialGuard — liquidez Qonto / deuda soberana (Lafayette, espejo).

- Cada petición HTTP reevalúa liquidez (entorno; sin bypass por reinicio salvo FINANCIAL_GUARD_SKIP).
- Umbral: DEUDA_TOTAL (default 145_500 €) frente a QONTO_BALANCE_EUR o anulación QONTO_PAGO_CONFIRMADO=1.
- Rutas de cobro/webhook permanecen en allowlist para poder regularizar.

Capa adicional: ``guard_stripe_call`` / ``resilient_stripe`` — reintentos en llamadas Stripe sin
apagar el servidor; ``log_sovereignty_event`` — trazabilidad (``monetizacion_trace_demo.log`` o
``MONETIZATION_LOG_PATH``).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parent.parent
_AUDIT_LOG = _ROOT / "logs" / "sovereignty_access_audit.jsonl"

# Rutas de espejo / sombra (auditoría comercial Lafayette).
_MIRROR_PREFIXES: tuple[str, ...] = (
    "/api/mirror_digital_event",
    "/mirror_digital_event",
    "/api/mirror_shadow_log",
    "/mirror_shadow_log",
)


def deuda_total_eur() -> float:
    raw = (os.environ.get("DEUDA_TOTAL") or "145500").strip().replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return 145500.0


def qonto_balance_eur() -> float | None:
    """None = no hay cifra operativa en env (se trata como bloqueo estricto)."""
    raw = (os.environ.get("QONTO_BALANCE_EUR") or "").strip().replace(",", ".")
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def qonto_pago_confirmado() -> bool:
    """Override manual de tesorería (luz verde sin depender solo del saldo en env)."""
    if (os.environ.get("FINANCIAL_GUARD_SKIP") or "").strip() == "1":
        return True
    v = (
        os.environ.get("QONTO_PAGO_CONFIRMADO")
        or os.environ.get("PAGO_CONFIRMADO_QONTO")
        or ""
    ).strip().lower()
    return v in ("1", "true", "yes")


def liquidity_ok() -> bool:
    if (os.environ.get("FINANCIAL_GUARD_SKIP") or "").strip() == "1":
        return True
    if qonto_pago_confirmado():
        return True
    threshold = deuda_total_eur()
    bal = qonto_balance_eur()
    if bal is None:
        return False
    return bal + 1e-9 >= threshold


def sovereignty_status() -> dict[str, Any]:
    """Estado lectura para Jules / CI; no sustituye auditoría contable."""
    ok = liquidity_ok()
    return {
        "liquidity_ok": ok,
        "sleep_mode": not ok,
        "pau_v11_commercial_unlocked": ok,
        "deuda_total_eur": deuda_total_eur(),
        "qonto_balance_eur": qonto_balance_eur(),
        "qonto_pago_confirmado": qonto_pago_confirmado(),
        "protocol": "sovereignty_v10_impago",
        "patent": "PCT/EP2025/067317",
    }


def is_mirror_request_path(path: str) -> bool:
    p = path or ""
    return any(p == pref or p.startswith(pref + "/") for pref in _MIRROR_PREFIXES)


def exit_after_mirror_402_enabled() -> bool:
    """
    Kill-switch tras 402 en ruta mirror: solo si la env está en ``1`` explícito.

    Por defecto **desactivado** (variables ausentes o vacías → no se llama ``os._exit``).
    Alias: ``FINANCIAL_GUARD_EXIT_AFTER_402`` (retrocompatible).
    """
    raw = (
        os.environ.get("FINANCIAL_GUARD_EXIT_AFTER_MIRROR_402")
        or os.environ.get("FINANCIAL_GUARD_EXIT_AFTER_402")
        or "0"
    )
    return str(raw).strip() == "1"


def _allowlist_path(path: str) -> bool:
    """Cobro inaugural, webhooks Stripe y estado soberano (monitor Jules); el resto → 402 si impago."""
    p = path or ""
    prefixes = (
        "/api/stripe_webhook_fr",
        "/stripe_webhook_fr",
        "/api/stripe_inauguration_checkout",
        "/stripe_inauguration_checkout",
        "/api/v1/falla/cobros",
        "/api/v1/falla/memories",
        "/api/sovereignty_guard_status",
        "/sovereignty_guard_status",
    )
    return any(p == pref or p.startswith(pref + "/") for pref in prefixes)


def _cors_json_response(payload: dict, status: int):
    from flask import Response

    body = json.dumps(payload, ensure_ascii=False)
    r = Response(body, status=status, mimetype="application/json; charset=utf-8")
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return r


def _cors_preflight_no_content() -> object:
    from flask import Response

    r = Response(status=204)
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    r.headers["Access-Control-Max-Age"] = "86400"
    return r


def _append_audit(record: dict) -> None:
    try:
        _AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with open(_AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        logger.warning("FinancialGuard: no se pudo escribir auditoría: %s", e)


def configure_boot_financial_guard(app) -> None:
    """
    Verificación al importar / crear la app Flask (inicio del servidor).

    - Sin liquidez Qonto (pago_confirmado_qonto / saldo vs DEUDA_TOTAL): el **servicio
      comercial** no se considera operativo. Por defecto el proceso **sí** arranca para
      que el middleware pueda responder **HTTP 402** a espejos y rutas no allowlist.
    - ``FINANCIAL_GUARD_STRICT_BOOT=1``: ``sys.exit(1)`` inmediato si no hay liquidez.
      No hay 402 posible (el servidor no llega a atender peticiones). Solo usar si se
      prefiere fallar el boot frente a un balanceador que devuelve 402 por otra vía.

    Tras el **primer** 402 en ruta espejo, cierre del proceso (opcional): solo con
    ``FINANCIAL_GUARD_EXIT_AFTER_MIRROR_402=1`` (por defecto **no** termina el worker).
    """
    ok = liquidity_ok()
    app.config["FINANCIAL_GUARD_LIQUIDITY_OK"] = ok
    if ok:
        logger.info("FinancialGuard: liquidez OK; arranque autorizado.")
        return

    msg = (
        "FinancialGuard CRÍTICO: impago o Qonto no verificado "
        "(QONTO_PAGO_CONFIRMADO / QONTO_BALANCE_EUR vs DEUDA_TOTAL). "
        "Servicio comercial suspendido."
    )
    logger.critical(msg)

    if (os.environ.get("FINANCIAL_GUARD_STRICT_BOOT") or "").strip() == "1":
        sys.exit(1)

    logger.critical(
        "FinancialGuard: API en modo 402 salvo allowlist (checkout Stripe FR, webhook, "
        "sovereignty_guard_status). Espejos tienda reciben 402 antes de cualquier lógica "
        "de espejo. Para cerrar el proceso tras el primer 402 en ruta mirror: "
        "FINANCIAL_GUARD_EXIT_AFTER_MIRROR_402=1."
    )


def register_financial_guard_middleware(app) -> None:
    """
    Lafayette / tienda: sin liquidez, 402 en todas las rutas salvo allowlist.
    Cada request vuelve a leer env (Vercel/servidor debe redeploy o actualizar vars).
    """
    _exit_lock = threading.Lock()
    _exit_scheduled = False

    @app.before_request
    def _financial_guard_before():  # type: ignore[name-defined]
        from flask import request

        if liquidity_ok():
            return None
        if _allowlist_path(request.path):
            return None
        if request.method == "OPTIONS":
            return _cors_preflight_no_content()

        request.environ["financial_guard_402"] = "1"
        total = deuda_total_eur()
        bal = qonto_balance_eur()
        payload = {
            "status": "payment_required",
            "error": "Payment Required",
            "message": (
                "Servicio suspendido: saldo Qonto insuficiente (Stripe u otros saldos no "
                "sustituyen Qonto regularizado). Regularizar según contrato."
            ),
            "deuda_total_eur": total,
            "qonto_balance_eur": bal,
            "patent": "PCT/EP2025/067317",
        }
        return _cors_json_response(payload, 402)

    @app.after_request
    def _financial_guard_after(response):  # type: ignore[name-defined]
        nonlocal _exit_scheduled
        from flask import request

        try:
            rec = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "path": request.path,
                "method": request.method,
                "remote_addr": request.remote_addr or "",
                "user_agent": (request.headers.get("User-Agent") or "")[:300],
                "mirror": is_mirror_request_path(request.path),
                "deuda_total_eur": deuda_total_eur(),
                "qonto_balance_eur": qonto_balance_eur(),
            }
            _append_audit(rec)
        except Exception as e:
            logger.debug("FinancialGuard audit: %s", e)

        if exit_after_mirror_402_enabled() and request.environ.get("financial_guard_402") == "1":
            if is_mirror_request_path(request.path) and response.status_code == 402:
                with _exit_lock:
                    if not _exit_scheduled:
                        _exit_scheduled = True
                        logger.critical(
                            "FinancialGuard: FINANCIAL_GUARD_EXIT_AFTER_MIRROR_402=1 → cierre proceso."
                        )

                        def _delayed_exit():
                            time.sleep(0.1)
                            os._exit(1)

                        threading.Thread(target=_delayed_exit, daemon=True).start()

        return response


# --- Stripe error resilience (retries; nunca sys.exit desde aquí) ---
_LOG_FILE = os.getenv(
    "MONETIZATION_LOG_PATH",
    os.path.join("/tmp", "monetizacion_trace_demo.log"),
)

_logger = logging.getLogger("financial_guard.stripe_resilience")
if not any(isinstance(h, (logging.FileHandler, logging.StreamHandler)) for h in _logger.handlers):
    try:
        _handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    except OSError:
        _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    _logger.addHandler(_handler)
_logger.setLevel(logging.INFO)

MAX_RETRIES: int = 3
RETRY_DELAY_S: float = 2.0


def guard_stripe_call(
    fn: Callable[..., Any],
    *args: Any,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY_S,
    **kwargs: Any,
) -> Any:
    """
    Envuelve una llamada Stripe con reintentos.
    Ante 402 u otro error, registra el fallo y reintenta.
    No llama a sys.exit() ni apaga el servidor.
    """
    last_error: Exception | None = None
    fn_name = getattr(fn, "__name__", fn.__class__.__name__)
    for attempt in range(1, max_retries + 1):
        try:
            result = fn(*args, **kwargs)
            if attempt > 1:
                _logger.info(
                    "stripe_call_recovered | fn=%s | attempt=%d",
                    fn_name,
                    attempt,
                )
            return result
        except Exception as exc:
            last_error = exc
            error_code = getattr(exc, "http_status", None) or "unknown"
            _logger.warning(
                "stripe_call_failed | fn=%s | attempt=%d/%d | status=%s | error=%s",
                fn_name,
                attempt,
                max_retries,
                error_code,
                str(exc)[:200],
            )
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)

    _logger.error(
        "stripe_call_exhausted | fn=%s | retries=%d | last_error=%s",
        fn_name,
        max_retries,
        str(last_error)[:300],
    )
    return None


def resilient_stripe(max_retries: int = MAX_RETRIES, retry_delay: float = RETRY_DELAY_S):
    """
    Versión decorador de guard_stripe_call.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return guard_stripe_call(
                fn, *args, max_retries=max_retries, retry_delay=retry_delay, **kwargs
            )

        return wrapper

    return decorator


def log_sovereignty_event(
    event_type: str,
    detail: str,
    session_id: str = "",
    amount_eur: float = 0.0,
) -> None:
    """Registro de evento soberano / financiero para auditoría."""
    _logger.info(
        "sovereignty_event | type=%s | session=%s | amount=%.2f | detail=%s",
        event_type,
        session_id,
        amount_eur,
        detail[:500],
    )
