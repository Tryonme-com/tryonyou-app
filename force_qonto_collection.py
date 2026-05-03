#!/usr/bin/env python3
"""
Force Qonto Collection — mode « asedio » (siege polling).

Polling continu du solde Qonto (et optionnellement Stripe) jusqu'à
détecter le crédit attendu ou un dépassement du seuil cible.

Actions à chaque cycle :
  1. GET /v2/organization → solde EUR
  2. GET Stripe Balance (optionnel) → solde disponible
  3. Comparaison avec TARGET_AMOUNT_EUR / TARGET_AMOUNT_CENTS
  4. Si match ou solde ≥ cible → notification Slack/Make + mise à jour Linear
  5. Si bloqué → retransmission de la lettre compliance (optionnel)

Variables d'environnement (voir .env.example) :
  QONTO_API_KEY (ou QONTO_LOGIN + QONTO_SECRET_KEY)
  QONTO_BASE_URL (défaut : https://thirdparty.qonto.com)
  QONTO_BANK_IBAN (optionnel, filtre sur IBAN)
  TARGET_AMOUNT_EUR / TARGET_AMOUNT_CENTS
  POLL_INTERVAL_SECONDS (défaut : 60)
  FORCE_COLLECTION_MAX_CYCLES (défaut : illimité, 0 = illimité)
  FORCE_COLLECTION_RETRANSMIT_EVERY (défaut : 10, retransmit email every N failed cycles)
  SLACK_WEBHOOK_URL / MAKE_WEBHOOK_URL
  STRIPE_SECRET_KEY_FR (optionnel, pour double vérification solde Stripe)

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
LOG_PATH = ROOT / "logs" / "force_qonto_collection.jsonl"

for _d in (ROOT / "api", ROOT / "logic"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("force_qonto_collection")

QONTO_PROD = "https://thirdparty.qonto.com"


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


def _env_int(key: str, default: int) -> int:
    raw = (os.getenv(key) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    raw = (os.getenv(key) or "").strip().replace(",", ".")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _qonto_auth() -> str:
    single = (os.getenv("QONTO_API_KEY") or "").strip()
    if single:
        return single
    login = (os.getenv("QONTO_LOGIN") or "").strip()
    secret = (os.getenv("QONTO_SECRET_KEY") or "").strip()
    if login and secret:
        return f"{login}:{secret}"
    return ""


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
        logger.warning("Webhook failed: %s", e)
        return False


def _append_log(record: dict) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("Log write error: %s", e)


def fetch_qonto_balance(
    auth: str,
    base_url: str,
    preferred_iban: str | None = None,
) -> dict:
    """
    Fetch Qonto organization data and return aggregated EUR balance.
    """
    import urllib.request as urlreq

    url = f"{base_url.rstrip('/')}/v2/organization"
    req = urlreq.Request(url, headers={
        "Authorization": auth,
        "Accept": "application/json",
    })
    try:
        with urlreq.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}

    org = data.get("organization") or {}
    accounts = org.get("bank_accounts") or data.get("bank_accounts") or []
    iban_norm = (preferred_iban or "").replace(" ", "").upper()

    total_cents = 0
    matched_accounts = []
    for acc in accounts:
        if not isinstance(acc, dict):
            continue
        cur = str(acc.get("currency") or "EUR").upper()
        if cur != "EUR":
            continue
        iban = str(acc.get("iban") or "").strip()
        if iban_norm and iban.replace(" ", "").upper() != iban_norm:
            continue
        balance_cents = int(acc.get("balance_cents", 0))
        total_cents += balance_cents
        matched_accounts.append({
            "iban_suffix": iban[-4:] if len(iban) >= 4 else "****",
            "balance_cents": balance_cents,
            "balance_eur": round(balance_cents / 100.0, 2),
        })

    return {
        "ok": True,
        "total_balance_cents": total_cents,
        "total_balance_eur": round(total_cents / 100.0, 2),
        "accounts": matched_accounts,
        "org_name": org.get("legal_name") or org.get("name") or "",
    }


def fetch_stripe_balance(currency: str = "eur") -> dict:
    """Optional Stripe balance check for dual verification."""
    try:
        import stripe
        sk = (
            os.getenv("STRIPE_SECRET_KEY_FR", "").strip()
            or os.getenv("STRIPE_SECRET_KEY", "").strip()
        )
        if not sk:
            return {"ok": False, "error": "no_stripe_key"}
        stripe.api_key = sk
        balance = stripe.Balance.retrieve()
        for item in (balance.get("available") or []):
            if str(item.get("currency", "")).lower() == currency.lower():
                cents = int(item.get("amount", 0))
                return {
                    "ok": True,
                    "available_cents": cents,
                    "available_eur": round(cents / 100.0, 2),
                    "currency": currency,
                }
        return {"ok": True, "available_cents": 0, "available_eur": 0.0, "currency": currency}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


def _try_retransmit_email() -> bool:
    """Attempt to retransmit the compliance letter (best-effort)."""
    try:
        from compliance_email_qonto import send_compliance_email
        return send_compliance_email(dry_run=False)
    except ImportError:
        logger.warning("compliance_email_qonto not importable; skip retransmit.")
        return False
    except Exception as e:
        logger.warning("Email retransmit failed: %s", e)
        return False


def run_collection_loop(
    *,
    target_cents: int,
    poll_seconds: int = 60,
    max_cycles: int = 0,
    retransmit_every: int = 10,
    webhook_url: str = "",
    check_stripe: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Main siege loop: poll Qonto balance until target is met.
    """
    auth = _qonto_auth()
    if not auth:
        msg = "Qonto auth missing: set QONTO_API_KEY or QONTO_LOGIN + QONTO_SECRET_KEY"
        logger.error(msg)
        return {"status": "error", "error": "missing_qonto_auth", "message": msg}

    base_url = (os.getenv("QONTO_BASE_URL") or QONTO_PROD).strip()
    preferred_iban = (os.getenv("QONTO_BANK_IBAN") or "").strip() or None
    target_eur = round(target_cents / 100.0, 2)

    logger.info(
        "Collection siege: target %.2f EUR (%d cents), poll %ds, max_cycles %s, retransmit every %d",
        target_eur, target_cents, poll_seconds,
        max_cycles if max_cycles > 0 else "unlimited",
        retransmit_every,
    )

    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now(timezone.utc).isoformat()
        logger.info("--- Cycle %d (target: %.2f EUR) ---", cycle, target_eur)

        qonto_result = fetch_qonto_balance(auth, base_url, preferred_iban)
        stripe_result = fetch_stripe_balance() if check_stripe else {"ok": False, "skipped": True}

        qonto_ok = qonto_result.get("ok", False)
        qonto_balance = qonto_result.get("total_balance_cents", 0) if qonto_ok else 0

        log_entry = {
            "ts": ts,
            "cycle": cycle,
            "target_cents": target_cents,
            "qonto": qonto_result,
            "stripe": stripe_result if check_stripe else None,
        }

        if qonto_ok and qonto_balance >= target_cents:
            logger.info(
                "TARGET MET: Qonto balance %d cents (%.2f EUR) >= target %d cents (%.2f EUR)",
                qonto_balance, qonto_balance / 100.0, target_cents, target_eur,
            )
            result = {
                "status": "target_met",
                "cycle": cycle,
                "qonto_balance_cents": qonto_balance,
                "qonto_balance_eur": round(qonto_balance / 100.0, 2),
                "target_cents": target_cents,
                "target_eur": target_eur,
                "ts": ts,
                "qonto": qonto_result,
            }
            _append_log({**log_entry, "action": "target_met"})
            _notify_webhook(webhook_url, {"event": "qonto_collection_target_met", **result})
            return result

        if not qonto_ok:
            logger.warning("Qonto API error: %s", qonto_result.get("error", "unknown"))
            _append_log({**log_entry, "action": "qonto_error"})
        else:
            logger.info(
                "Balance: %d cents (%.2f EUR) — need %d more cents",
                qonto_balance, qonto_balance / 100.0, target_cents - qonto_balance,
            )
            _append_log({**log_entry, "action": "waiting"})

        if retransmit_every > 0 and cycle % retransmit_every == 0 and not dry_run:
            logger.info("Retransmitting compliance email (cycle %d)…", cycle)
            _try_retransmit_email()

        if max_cycles > 0 and cycle >= max_cycles:
            result = {
                "status": "max_cycles_reached",
                "cycle": cycle,
                "qonto_balance_cents": qonto_balance,
                "target_cents": target_cents,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            _append_log({**result, "action": "max_cycles_reached"})
            _notify_webhook(webhook_url, {"event": "qonto_collection_max_cycles", **result})
            logger.warning("Max cycles (%d) reached without meeting target.", max_cycles)
            return result

        if dry_run:
            return {
                "status": "dry_run",
                "cycle": cycle,
                "qonto": qonto_result,
                "stripe": stripe_result if check_stripe else None,
                "target_cents": target_cents,
            }

        try:
            time.sleep(poll_seconds)
        except KeyboardInterrupt:
            logger.info("Interrupted by user (Ctrl+C).")
            return {
                "status": "interrupted",
                "cycle": cycle,
                "qonto_balance_cents": qonto_balance,
                "target_cents": target_cents,
            }


def main() -> int:
    _merge_dotenv()

    parser = argparse.ArgumentParser(
        description="Force Qonto Collection — siege polling until balance target is met."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Execute one cycle without retransmit and exit",
    )
    parser.add_argument(
        "--max-cycles", type=int, default=None,
        help="Override max cycle count (0 = unlimited)",
    )
    parser.add_argument(
        "--check-stripe", action="store_true",
        help="Also check Stripe balance each cycle",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single cycle and exit",
    )
    args = parser.parse_args()

    target_eur = _env_float("TARGET_AMOUNT_EUR", 557644.20)
    target_cents_raw = (os.getenv("TARGET_AMOUNT_CENTS") or "").strip()
    if target_cents_raw.isdigit():
        target_cents = int(target_cents_raw)
    else:
        target_cents = int(round(target_eur * 100.0 + 1e-9))

    poll = max(5, _env_int("POLL_INTERVAL_SECONDS", 60))
    max_cycles = args.max_cycles if args.max_cycles is not None else _env_int("FORCE_COLLECTION_MAX_CYCLES", 0)
    retransmit_every = _env_int("FORCE_COLLECTION_RETRANSMIT_EVERY", 10)
    webhook = (
        os.getenv("SLACK_WEBHOOK_URL", "").strip()
        or os.getenv("MAKE_WEBHOOK_URL", "").strip()
    )

    if args.once:
        max_cycles = 1
    if args.dry_run:
        max_cycles = 1

    result = run_collection_loop(
        target_cents=target_cents,
        poll_seconds=poll,
        max_cycles=max_cycles,
        retransmit_every=retransmit_every,
        webhook_url=webhook,
        check_stripe=args.check_stripe,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    status = result.get("status", "")
    if status == "target_met":
        return 0
    if status in ("dry_run", "interrupted"):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
