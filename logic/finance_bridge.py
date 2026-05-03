"""
FinanceBridge — Stripe LIVE (payout) + comprobación Qonto / tesorería / auditoría V11.

- Carga entorno desde la raíz del repo: .env.production y luego .env.
- Clave Stripe: prioridad api/stripe_fr_resolve.py (FR, luego legado).
  Acepta sk_live_ (secreta) o rk_live_ (restricted) con permisos de payouts.
- Payout real: solo si FINANCE_BRIDGE_LIVE_PAYOUT=1.
- Reintentos Stripe: FINANCE_BRIDGE_PAYOUT_USE_RETRIES=1 (cli), FINANCE_BRIDGE_MAX_ATTEMPTS,
  FINANCE_BRIDGE_RETRY_DELAY_SECONDS, FINANCE_BRIDGE_IDEMPOTENCY_KEY (opcional).
- Tras crear payout: FINANCE_BRIDGE_POLL_UNTIL_PAID=1 hace polling con
  ``stripe.Payout.retrieve`` hasta ``status=paid`` (o fallo/cancelación).
- Metadata Stripe incluye ``try_payout_now=1`` para trazabilidad operativa.
- Puerta audit_log_v11.txt: exige señal MATCHED vía scripts/parse_audit_log_v11.py
  (función audit_reconciliation_matched); FINANCE_BRIDGE_SKIP_AUDIT_LOG=1 solo en lab.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import requests
import stripe
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[1]
_API = _ROOT / "api"
_SCRIPTS = _ROOT / "scripts"
for _d in (_API, _SCRIPTS):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

try:
    from stripe_fr_resolve import resolve_stripe_secret_fr
except ImportError:
    resolve_stripe_secret_fr = None  # type: ignore[assignment,misc]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("FinanceBridge")

_QONTO_ORG_URL = "https://thirdparty.qonto.com/v2/organization"
_PARSE_AUDIT_SPEC = _SCRIPTS / "parse_audit_log_v11.py"


def _load_parse_audit_module() -> Any:
    spec = importlib.util.spec_from_file_location("parse_audit_log_v11", _PARSE_AUDIT_SPEC)
    if spec is None or spec.loader is None:
        raise ImportError("No se pudo cargar parse_audit_log_v11.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_env_files() -> None:
    for name in (".env.production", ".env"):
        p = _ROOT / name
        if p.is_file():
            load_dotenv(p, override=False)


def _resolve_stripe_live_key() -> str:
    if resolve_stripe_secret_fr is not None:
        return (resolve_stripe_secret_fr() or "").strip()
    return (
        os.getenv("STRIPE_SECRET_KEY_FR", "").strip()
        or os.getenv("STRIPE_SECRET_KEY_NUEVA", "").strip()
        or os.getenv("STRIPE_SECRET_KEY", "").strip()
    )


def _stripe_live_key_allowed(key: str) -> bool:
    return bool(key) and (key.startswith("sk_live_") or key.startswith("rk_live_"))


def _audit_log_gate_ok() -> bool:
    """True si audit_log_v11.txt contiene señal MATCHED y sin bloqueos negativos."""
    if (os.getenv("FINANCE_BRIDGE_SKIP_AUDIT_LOG") or "").strip() == "1":
        logger.warning("FINANCE_BRIDGE_SKIP_AUDIT_LOG=1: se omite puerta audit_log_v11.")
        return True
    rel = (os.getenv("FINANCE_BRIDGE_AUDIT_LOG") or "audit_log_v11.txt").strip()
    audit_path = Path(rel) if Path(rel).is_absolute() else (_ROOT / rel)
    try:
        mod = _load_parse_audit_module()
        matched, reason = mod.audit_reconciliation_matched(audit_path)
    except Exception as exc:
        logger.error("No se pudo evaluar auditoría V11: %s", exc)
        return False
    if not matched:
        logger.error("Auditoría V11 no MATCHED: %s (fichero: %s)", reason, audit_path)
        return False
    logger.info("Auditoría V11 OK (%s): %s", reason, audit_path)
    return True


def _treasury_reconciliation_ok() -> bool:
    """True si el informe de compliance indica liquidez alineada (MATCHED / OK)."""
    if (os.getenv("FINANCE_BRIDGE_SKIP_TREASURY_CHECK") or "").strip() == "1":
        logger.warning("FINANCE_BRIDGE_SKIP_TREASURY_CHECK=1: se omite cruce con financial_compliance.")
        return True
    try:
        from financial_compliance import build_financial_reconciliation_report
    except ImportError:
        logger.warning("financial_compliance no importable; tesorería no verificada por informe.")
        return False

    rep = build_financial_reconciliation_report()
    if str(rep.get("reconciliation_status") or "").upper() != "OK":
        return False
    rec = rep.get("reconciliation") or {}
    if rec.get("payout_blocked") is True:
        return False
    return rec.get("status") in ("MATCHED", "BUFFER_RINGFENCED")


def _log_stripe_permission_error(exc: stripe.error.StripeError, *, context: str) -> None:
    logger.error(
        "%s Stripe permisos o clave limitada: type=%s code=%s http_status=%s user_message=%s",
        context,
        type(exc).__name__,
        getattr(exc, "code", None),
        getattr(exc, "http_status", None),
        (getattr(exc, "user_message", None) or str(exc))[:500],
    )


class FinancialEngine:
    def __init__(self) -> None:
        _load_env_files()
        self.stripe_key = _resolve_stripe_live_key()
        self.qonto_api_key = (os.getenv("QONTO_API_KEY") or os.getenv("QONTO_AUTHORIZATION_KEY") or "").strip()
        self.qonto_iban = (os.getenv("QONTO_IBAN") or "").strip()
        self.bridge_id = (os.getenv("BRIDGE_CLIENT_ID") or "").strip()

        if not _stripe_live_key_allowed(self.stripe_key):
            raise ConnectionError(
                "CRÍTICO: se requiere clave Stripe LIVE (sk_live_ secreta o rk_live_ restricted "
                "con permiso payouts:write). Defina STRIPE_SECRET_KEY_FR o STRIPE_SECRET_KEY."
            )

        stripe.api_key = self.stripe_key

    def check_treasury_reserve(self, amount_cents: int) -> bool:
        """
        Valida auditoría V11 (audit_log) y tesorería (financial_compliance) antes del payout.
        """
        amount_eur = round(amount_cents / 100.0, 2)
        logger.info("Validando auditoría + reserva para payout de %.2f EUR", amount_eur)
        if not _audit_log_gate_ok():
            return False
        ok = _treasury_reconciliation_ok()
        if not ok:
            logger.error("Treasury / reconciliation no OK; payout no autorizado por motor.")
        return ok

    def execute_payout(self, amount_cents: int, currency: str = "eur") -> Any | None:
        """Crea un payout Stripe hacia la cuenta bancaria por defecto (p. ej. IBAN Qonto vinculado)."""
        if (os.getenv("FINANCE_BRIDGE_LIVE_PAYOUT") or "").strip() != "1":
            logger.warning(
                "Payout no ejecutado: defina FINANCE_BRIDGE_LIVE_PAYOUT=1 para crear payout real en Stripe."
            )
            return None

        if not self.check_treasury_reserve(amount_cents):
            return None

        idem = (os.getenv("FINANCE_BRIDGE_IDEMPOTENCY_KEY") or "").strip() or f"finbridge-{amount_cents}-{uuid.uuid4().hex[:24]}"
        created = self._execute_stripe_payout_only(amount_cents, currency, idempotency_key=idem)
        return self._maybe_poll_payout_to_paid(created) if created is not None else None

    def _execute_stripe_payout_only(
        self,
        amount_cents: int,
        currency: str,
        *,
        idempotency_key: str,
    ) -> Any | None:
        meta: dict[str, str] = {
            "sync": "pending",
            "source": "logic.finance_bridge",
            "target": "qonto_linked",
            "try_payout_now": "1",
        }
        if self.bridge_id:
            meta["bridge_id"] = self.bridge_id

        try:
            payout = stripe.Payout.create(
                amount=amount_cents,
                currency=currency.lower(),
                statement_descriptor="TRYONYOU-APP-LIVE"[:22],
                metadata=meta,
                idempotency_key=idempotency_key[:255],
            )
            logger.info("Payout iniciado: %s", getattr(payout, "id", payout))
            return payout
        except stripe.error.PermissionError as exc:
            _log_stripe_permission_error(exc, context="PermissionError (restricted key / access limited)")
            return None
        except stripe.error.InvalidRequestError as exc:
            raw = (getattr(exc, "user_message", None) or str(exc)).lower()
            if any(
                s in raw
                for s in (
                    "does not have access",
                    "restricted",
                    "cannot create a payout",
                    "this account",
                    "permission",
                )
            ):
                _log_stripe_permission_error(exc, context="InvalidRequestError (permisos)")
                return None
            logger.error("Stripe InvalidRequestError: %s", getattr(exc, "user_message", None) or exc)
            return None
        except stripe.error.AuthenticationError as exc:
            _log_stripe_permission_error(exc, context="AuthenticationError")
            return None
        except stripe.error.StripeError as exc:
            logger.error("Stripe error: type=%s %s", type(exc).__name__, getattr(exc, "user_message", None) or exc)
            return None
        except Exception as exc:
            logger.error("Error inesperado en Stripe Payout: %s", exc)
            return None

    def _wait_stripe_payout_paid(self, payout_id: str) -> str:
        """
        Poll ``Payout.retrieve`` hasta ``paid``, ``failed``, ``canceled`` o timeout.
        Devuelve el ``status`` final (p. ej. ``paid``) o ``timeout``.
        """
        interval = float((os.getenv("FINANCE_BRIDGE_PAYOUT_POLL_INTERVAL_SEC") or "15").strip() or "15")
        max_sec = float((os.getenv("FINANCE_BRIDGE_PAYOUT_POLL_MAX_SEC") or str(72 * 3600)).strip() or str(72 * 3600))
        deadline = time.time() + max(60.0, max_sec)
        interval = max(3.0, interval)
        last_status = "unknown"
        while time.time() < deadline:
            try:
                po = stripe.Payout.retrieve(payout_id)
                last_status = str(getattr(po, "status", "") or "")
                if last_status == "paid":
                    logger.info("Payout %s en estado paid.", payout_id)
                    return "paid"
                if last_status in ("failed", "canceled"):
                    logger.error("Payout %s terminó en estado %s.", payout_id, last_status)
                    return last_status
                logger.info("Payout %s estado=%s; reintento en %.0fs …", payout_id, last_status, interval)
            except stripe.error.StripeError as exc:
                logger.warning("Retrieve payout %s: %s", payout_id, getattr(exc, "user_message", None) or exc)
            time.sleep(interval)
        logger.error("Timeout esperando paid para payout %s (último estado=%s).", payout_id, last_status)
        return "timeout"

    def _maybe_poll_payout_to_paid(self, payout: Any) -> Any:
        if (os.getenv("FINANCE_BRIDGE_POLL_UNTIL_PAID") or "").strip() != "1":
            return payout
        pid = getattr(payout, "id", None)
        if not pid:
            return payout
        final = self._wait_stripe_payout_paid(str(pid))
        if final != "paid":
            logger.warning(
                "Payout %s creado pero estado final de polling=%s (revisar Dashboard Stripe / banco).",
                pid,
                final,
            )
        return payout

    def execute_payout_with_retries(
        self,
        amount_cents: int,
        currency: str = "eur",
        *,
        max_attempts: int | None = None,
        delay_seconds: float | None = None,
    ) -> Any | None:
        """
        Tras validar tesorería una sola vez, reintenta Stripe.Payout.create hasta éxito o agotar intentos.
        Usa una idempotency_key fija por sesión para no duplicar payouts si Stripe aceptó en red parcial.
        """
        if (os.getenv("FINANCE_BRIDGE_LIVE_PAYOUT") or "").strip() != "1":
            logger.warning(
                "Payout no ejecutado: defina FINANCE_BRIDGE_LIVE_PAYOUT=1 para crear payout real en Stripe."
            )
            return None
        if not self.check_treasury_reserve(amount_cents):
            return None
        n = max_attempts if max_attempts is not None else max(1, int((os.getenv("FINANCE_BRIDGE_MAX_ATTEMPTS") or "25").strip() or "25"))
        delay = delay_seconds if delay_seconds is not None else float((os.getenv("FINANCE_BRIDGE_RETRY_DELAY_SECONDS") or "12").strip() or "12")
        idem = (os.getenv("FINANCE_BRIDGE_IDEMPOTENCY_KEY") or "").strip() or f"finbridge-retry-{amount_cents}-{uuid.uuid4().hex[:32]}"
        for attempt in range(1, n + 1):
            payout = self._execute_stripe_payout_only(amount_cents, currency, idempotency_key=idem)
            if payout is not None and getattr(payout, "id", None):
                return self._maybe_poll_payout_to_paid(payout)
            logger.warning(
                "Reintento payout Stripe (%s/%s) tras %ss (idem prefix=%s…)",
                attempt,
                n,
                delay,
                idem[:16],
            )
            if attempt < n:
                time.sleep(max(1.0, delay))
        return None

    def sync_qonto_metadata(self, payout_id: str, *, amount_cents: int | None = None) -> bool:
        """
        Verifica credencial Qonto (GET organization) y deja constancia del payout (metadata bridge).
        """
        logger.info("Sincronizando payout %s con puente Qonto (metadata) …", payout_id)
        if not self.qonto_api_key:
            logger.warning("QONTO_API_KEY ausente: no se llama a thirdparty.qonto.com.")
            return False
        headers = {
            "Authorization": self.qonto_api_key,
            "Accept": "application/json",
        }
        try:
            r = requests.get(_QONTO_ORG_URL, headers=headers, timeout=45)
            r.raise_for_status()
        except Exception as exc:
            logger.error("Qonto organization check falló: %s", exc)
            return False

        amt_eur = round((amount_cents or 0) / 100.0, 2) if amount_cents else None
        payload: dict[str, Any] = {
            "external_id": payout_id,
            "source": "Stripe_Live_Payout",
            "qonto_reachable": True,
            "amount_eur": amt_eur,
            "iban_hint": self.qonto_iban or None,
            "next_step": "python3 scripts/qonto_metadata_bridge.py",
        }
        logger.info("Bridge metadata constancia: %s", payload)
        return True


if __name__ == "__main__":
    try:
        engine = FinancialEngine()
    except ConnectionError as e:
        print(str(e))
        raise SystemExit(2) from e

    # 1.500,00 EUR en céntimos (objetivo despliegue seguro hacia Qonto)
    monto_a_cobrar = int((os.getenv("FINANCE_BRIDGE_AMOUNT_CENTS") or "150000").strip())

    print("--- INICIANDO PROTOCOLO DE DESBLOQUEO FINANCIERO ---")
    use_retries = (os.getenv("FINANCE_BRIDGE_PAYOUT_USE_RETRIES") or "").strip() == "1"
    payout_result = (
        engine.execute_payout_with_retries(monto_a_cobrar)
        if use_retries
        else engine.execute_payout(monto_a_cobrar)
    )

    if payout_result:
        engine.sync_qonto_metadata(payout_result.id, amount_cents=monto_a_cobrar)
        dest = engine.qonto_iban or "cuenta Stripe por defecto"
        print(
            f"--- PROCESO COMPLETADO: payout {payout_result.id} "
            f"hacia destino bancario vinculado ({dest}) ---"
        )
    else:
        print("--- PROCESO NO EJECUTADO O FALLIDO: revisa audit log, compliance, FINANCE_BRIDGE_LIVE_PAYOUT y logs ---")
