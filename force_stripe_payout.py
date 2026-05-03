#!/usr/bin/env python3
"""
Force Stripe Payout — mode « try_payout_now » avec retries.

Tente de créer un payout Stripe vers le compte bancaire lié (Qonto)
en boucle jusqu'à obtenir un statut de succès ou épuiser les tentatives.

Ce script est complémentaire de logic/finance_bridge.py (FinancialEngine) ;
il ajoute une couche de retry agressive et de notification Make/Slack.

Variables d'environnement :
  STRIPE_SECRET_KEY_FR (ou STRIPE_SECRET_KEY) — clé sk_live_ ou rk_live_
  FORCE_PAYOUT_AMOUNT_CENTS — montant en centimes (défaut : env FINANCE_BRIDGE_AMOUNT_CENTS ou 150000)
  FORCE_PAYOUT_CURRENCY — devise (défaut : eur)
  FORCE_PAYOUT_MAX_RETRIES — tentatives max (défaut : 10)
  FORCE_PAYOUT_RETRY_DELAY — délai base en secondes (défaut : 30)
  FORCE_PAYOUT_DESCRIPTOR — libellé relevé (défaut : TRYONYOU-PAYOUT, max 22 chars)
  SLACK_WEBHOOK_URL / MAKE_WEBHOOK_URL — notification optionnelle
  FORCE_PAYOUT_DRY_RUN — 1 = simulation sans appel Stripe réel

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "logs" / "force_stripe_payout.jsonl"

for _d in (ROOT / "api", ROOT / "logic"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("force_stripe_payout")


def _merge_dotenv() -> None:
    for name in (".env.production", ".env"):
        p = ROOT / name
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def _resolve_stripe_key() -> str:
    try:
        from stripe_fr_resolve import resolve_stripe_secret_fr
        key = (resolve_stripe_secret_fr() or "").strip()
        if key:
            return key
    except ImportError:
        pass
    return (
        os.getenv("STRIPE_SECRET_KEY_FR", "").strip()
        or os.getenv("STRIPE_SECRET_KEY_NUEVA", "").strip()
        or os.getenv("STRIPE_SECRET_KEY", "").strip()
    )


def _env_int(key: str, default: int) -> int:
    raw = (os.getenv(key) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _notify_webhook(url: str, payload: dict) -> bool:
    if not url:
        return False
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        logger.warning("Webhook notify failed: %s", e)
        return False


def _append_log(record: dict) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("Log write error: %s", e)


def _check_balance(stripe_mod, currency: str) -> int:
    """Returns available balance in cents for the given currency."""
    try:
        balance = stripe_mod.Balance.retrieve()
        for item in (balance.get("available") or []):
            if str(item.get("currency", "")).lower() == currency.lower():
                return int(item.get("amount", 0))
    except Exception as e:
        logger.warning("Balance check failed: %s", e)
    return 0


def try_payout_now(
    *,
    amount_cents: int,
    currency: str = "eur",
    max_retries: int = 10,
    retry_delay: float = 30.0,
    descriptor: str = "TRYONYOU-PAYOUT",
    dry_run: bool = False,
    webhook_url: str = "",
) -> dict:
    """
    Attempt a Stripe payout with exponential-backoff retries.
    Returns a dict with the final status and payout details.
    """
    import stripe

    sk = _resolve_stripe_key()
    if not sk:
        msg = "No Stripe secret key found. Set STRIPE_SECRET_KEY_FR."
        logger.error(msg)
        return {"status": "error", "error": "missing_stripe_key", "message": msg}

    if not (sk.startswith("sk_live_") or sk.startswith("rk_live_") or sk.startswith("sk_test_")):
        msg = f"Stripe key prefix not recognized: {sk[:8]}…"
        logger.error(msg)
        return {"status": "error", "error": "invalid_stripe_key", "message": msg}

    stripe.api_key = sk
    amount_eur = round(amount_cents / 100.0, 2)
    logger.info(
        "Force payout: %.2f EUR (%d cents), max %d retries, delay %.0fs, dry_run=%s",
        amount_eur, amount_cents, max_retries, retry_delay, dry_run,
    )

    available = _check_balance(stripe, currency)
    logger.info("Stripe available balance (%s): %d cents (%.2f EUR)", currency, available, available / 100.0)

    if dry_run:
        result = {
            "status": "dry_run",
            "amount_cents": amount_cents,
            "currency": currency,
            "available_balance_cents": available,
            "stripe_key_prefix": sk[:12] + "…",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("DRY RUN — no payout created. %s", json.dumps(result))
        _append_log({**result, "action": "dry_run"})
        return result

    last_error = None
    for attempt in range(1, max_retries + 1):
        logger.info("Payout attempt %d/%d…", attempt, max_retries)

        try:
            payout = stripe.Payout.create(
                amount=amount_cents,
                currency=currency.lower(),
                statement_descriptor=descriptor[:22],
                metadata={
                    "source": "force_stripe_payout",
                    "attempt": str(attempt),
                    "patent": "PCT/EP2025/067317",
                    "protocol": "try_payout_now",
                },
            )

            payout_dict = dict(payout) if hasattr(payout, "items") else {"id": getattr(payout, "id", str(payout))}
            payout_id = payout_dict.get("id", "unknown")
            payout_status = payout_dict.get("status", "unknown")

            logger.info(
                "Payout created: id=%s status=%s (attempt %d)",
                payout_id, payout_status, attempt,
            )

            result = {
                "status": "success",
                "payout_id": payout_id,
                "payout_status": payout_status,
                "amount_cents": amount_cents,
                "currency": currency,
                "attempt": attempt,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            _append_log({**result, "action": "payout_created"})
            _notify_webhook(webhook_url, {"event": "force_payout_success", **result})

            try:
                from empire_payout_trans import register_payout_transition
                register_payout_transition(
                    amount_eur=amount_eur,
                    recipient="QONTO_FORCE_PAYOUT",
                    concept="force_stripe_payout_v10",
                    flow_token="try_payout_now",
                    session_id=payout_id,
                    source="force_stripe_payout",
                )
            except Exception:
                pass

            return result

        except Exception as exc:
            last_error = exc
            error_code = getattr(exc, "http_status", None) or "unknown"
            error_msg = (getattr(exc, "user_message", None) or str(exc))[:500]
            logger.warning(
                "Payout attempt %d/%d failed: status=%s error=%s",
                attempt, max_retries, error_code, error_msg,
            )
            _append_log({
                "action": "payout_attempt_failed",
                "attempt": attempt,
                "error_code": str(error_code),
                "error": error_msg,
                "ts": datetime.now(timezone.utc).isoformat(),
            })

            if attempt < max_retries:
                wait = min(retry_delay * (1.5 ** (attempt - 1)), 300)
                logger.info("Retrying in %.0f seconds…", wait)
                time.sleep(wait)

    result = {
        "status": "exhausted",
        "error": str(last_error)[:500] if last_error else "unknown",
        "attempts": max_retries,
        "amount_cents": amount_cents,
        "currency": currency,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    _append_log({**result, "action": "retries_exhausted"})
    _notify_webhook(webhook_url, {"event": "force_payout_exhausted", **result})
    logger.error("All %d payout attempts exhausted.", max_retries)
    return result


def main() -> int:
    _merge_dotenv()

    parser = argparse.ArgumentParser(
        description="Force Stripe Payout — try_payout_now mode with retries."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Check balance and key without creating a payout",
    )
    parser.add_argument(
        "--amount-cents", type=int, default=None,
        help="Override payout amount in cents",
    )
    parser.add_argument(
        "--max-retries", type=int, default=None,
        help="Override max retry count",
    )
    args = parser.parse_args()

    amount = args.amount_cents or _env_int(
        "FORCE_PAYOUT_AMOUNT_CENTS",
        _env_int("FINANCE_BRIDGE_AMOUNT_CENTS", 150000),
    )
    max_retries = args.max_retries or _env_int("FORCE_PAYOUT_MAX_RETRIES", 10)
    retry_delay = float(_env_int("FORCE_PAYOUT_RETRY_DELAY", 30))
    currency = (os.getenv("FORCE_PAYOUT_CURRENCY") or "eur").strip().lower()
    descriptor = (os.getenv("FORCE_PAYOUT_DESCRIPTOR") or "TRYONYOU-PAYOUT").strip()[:22]
    webhook = (
        os.getenv("SLACK_WEBHOOK_URL", "").strip()
        or os.getenv("MAKE_WEBHOOK_URL", "").strip()
    )
    dry_run = args.dry_run or (os.getenv("FORCE_PAYOUT_DRY_RUN", "").strip() == "1")

    result = try_payout_now(
        amount_cents=amount,
        currency=currency,
        max_retries=max_retries,
        retry_delay=retry_delay,
        descriptor=descriptor,
        dry_run=dry_run,
        webhook_url=webhook,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("success", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
