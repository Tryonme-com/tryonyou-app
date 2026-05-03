#!/usr/bin/env python3
"""
Asedio controlado Qonto: polling hasta validar ingreso (transacción objetivo o umbral de saldo).

Modos (FORCE_QONTO_COLLECTION_MODE):
  transaction  — igual que master_sync: importe TARGET_AMOUNT_* en transacciones crédito completadas
  balance      — suma balance_cents / balance de cuentas EUR hasta FORCE_QONTO_MIN_BALANCE_CENTS

Opcional: cada N ciclos fallidos re-lanza el envío de carta (subproceso, no import circular).

Variables: mismas que master_sync (QONTO_API_KEY o QONTO_LOGIN+SECRET, QONTO_BASE_URL, QONTO_BANK_IBAN,
  TARGET_AMOUNT_EUR, TARGET_AMOUNT_CENTS, POLL_INTERVAL_SECONDS).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "logs" / "force_qonto_collection.jsonl"

LOG = logging.getLogger("force_qonto_collection")


def _load_env() -> None:
    for name in (".env.production", ".env"):
        p = ROOT / name
        if p.is_file():
            load_dotenv(p, override=False)


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def _log_json(payload: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.open("a", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False) + "\n")


def _qonto_auth() -> str:
    single = (os.environ.get("QONTO_API_KEY") or "").strip()
    if single:
        return single
    login = (os.environ.get("QONTO_LOGIN") or "").strip()
    secret = (os.environ.get("QONTO_SECRET_KEY") or "").strip()
    if login and secret:
        return f"{login}:{secret}"
    return ""


def _float_env(name: str, default: float) -> float:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    s = raw.replace(" ", "")
    try:
        if s.count(",") == 1 and s.count(".") == 0:
            return float(s.replace(",", "."))
        return float(s.replace(",", "."))
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw, 10)
    except ValueError:
        return default


def _sum_eur_balance_cents(org: dict[str, Any], preferred_iban: str | None) -> tuple[int, list[dict[str, Any]]]:
    org_block = org.get("organization")
    accounts: list[Any] = []
    if isinstance(org_block, dict) and isinstance(org_block.get("bank_accounts"), list):
        accounts.extend(org_block["bank_accounts"])
    if isinstance(org.get("bank_accounts"), list):
        accounts.extend(org["bank_accounts"])
    iban_norm = (preferred_iban or "").replace(" ", "").upper()
    total = 0
    details: list[dict[str, Any]] = []
    for acc in accounts:
        if not isinstance(acc, dict):
            continue
        if str(acc.get("currency") or "EUR").upper() != "EUR":
            continue
        iban = str(acc.get("iban") or "").replace(" ", "").upper()
        if iban_norm and iban != iban_norm:
            continue
        cents = acc.get("balance_cents")
        if cents is not None:
            try:
                c = int(cents, 10) if isinstance(cents, str) else int(cents)
            except (TypeError, ValueError):
                c = 0
        else:
            bal = acc.get("balance")
            try:
                c = int(round(float(str(bal).replace(",", ".")) * 100))
            except (TypeError, ValueError):
                c = 0
        total += c
        details.append({"id": acc.get("id"), "iban_tail": (iban or "")[-4:], "balance_cents": c})
    return total, details


def _maybe_resend_letter(cycle: int, every: int) -> None:
    if every <= 0 or cycle % every != 0:
        return
    script = ROOT / "enviar_carta_qonto_compliance.py"
    if not script.is_file():
        return
    LOG.warning("Re-lanzando carta compliance (ciclo %s, cada %s ciclos).", cycle, every)
    try:
        subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            check=False,
            timeout=120,
        )
    except OSError as e:
        LOG.warning("Subproceso carta falló: %s", e)


def main() -> int:
    _setup_logging()
    _load_env()
    ap = argparse.ArgumentParser(description="Polling Qonto hasta condición de cobro / saldo.")
    ap.add_argument("--max-cycles", type=int, default=None, help="Límite de ciclos (default: ilimitado)")
    ap.add_argument("--once", action="store_true", help="Un solo ciclo y salir")
    args = ap.parse_args()

    auth = _qonto_auth()
    if not auth:
        LOG.error("Sin QONTO_API_KEY ni QONTO_LOGIN+QONTO_SECRET_KEY.")
        return 1

    mode = (os.environ.get("FORCE_QONTO_COLLECTION_MODE") or "transaction").strip().lower()
    base = (os.environ.get("QONTO_BASE_URL") or "https://thirdparty.qonto.com").rstrip("/")
    poll = max(5, _int_env("POLL_INTERVAL_SECONDS", _int_env("FORCE_QONTO_POLL_SECONDS", 60)))
    bank_iban = (os.environ.get("QONTO_BANK_IBAN") or "").strip() or None
    min_balance = _int_env("FORCE_QONTO_MIN_BALANCE_CENTS", 1)
    resend_every = _int_env("FORCE_QONTO_RESEND_LETTER_EVERY_N_CYCLES", 0)

    sys.path.insert(0, str(ROOT))
    from master_sync import (  # noqa: E402
        QontoContext,
        find_matching_transaction_cents,
        get_organization,
    )

    ctx = QontoContext(auth_value=auth, base_url=base)
    target_eur = _float_env("TARGET_AMOUNT_EUR", 557_644.20)
    target_cents = int(round(target_eur * 100))
    cents_raw = (os.environ.get("TARGET_AMOUNT_CENTS") or "").strip()
    if cents_raw.isdigit():
        target_cents = int(cents_raw, 10)

    cycle = 0

    while True:
        cycle += 1
        if args.max_cycles is not None and cycle > args.max_cycles:
            LOG.info("Máximo de ciclos alcanzado (%s).", args.max_cycles)
            return 3

        try:
            with httpx.Client(timeout=60.0) as client:
                org_cache = get_organization(ctx, client)

                if mode == "balance":
                    total_cents, details = _sum_eur_balance_cents(org_cache, bank_iban)
                    snap = {
                        "event": "force_qonto_poll_balance",
                        "cycle": cycle,
                        "total_balance_cents": total_cents,
                        "min_required_cents": min_balance,
                        "accounts": details,
                    }
                    _log_json(snap)
                    LOG.info(
                        "Saldo EUR agregado (céntimos)=%s (objetivo mínimo=%s)",
                        total_cents,
                        min_balance,
                    )
                    if total_cents >= min_balance:
                        done = {
                            "event": "force_qonto_balance_ok",
                            "cycle": cycle,
                            "total_balance_cents": total_cents,
                        }
                        _log_json(done)
                        print(json.dumps(done, ensure_ascii=False, indent=2))
                        return 0
                else:
                    match = find_matching_transaction_cents(
                        ctx, client, org_cache, target_cents, bank_iban
                    )
                    if match:
                        done = {
                            "event": "force_qonto_transaction_matched",
                            "cycle": cycle,
                            "target_cents": target_cents,
                            "bank_account_id": match.get("bank_account_id"),
                            "transaction": (match.get("transaction") or {}),
                        }
                        _log_json(done)
                        print(json.dumps(done, ensure_ascii=False, indent=2))
                        return 0
                    pend = {
                        "event": "force_qonto_poll_transaction",
                        "cycle": cycle,
                        "target_cents": target_cents,
                    }
                    _log_json(pend)
                    LOG.info("Sin transacción crédito %s céntimos; reintento.", target_cents)

        except (RuntimeError, httpx.HTTPError, OSError) as e:
            LOG.warning("Ciclo falló: %s", e)
            _log_json({"event": "force_qonto_poll_error", "cycle": cycle, "error": str(e)[:400]})

        _maybe_resend_letter(cycle, resend_every)

        if args.once:
            LOG.info("Modo --once: salida tras primer ciclo sin éxito.")
            return 2

        LOG.info("Esperando %s s…", poll)
        try:
            time.sleep(poll)
        except KeyboardInterrupt:
            LOG.info("Interrumpido por usuario.")
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
