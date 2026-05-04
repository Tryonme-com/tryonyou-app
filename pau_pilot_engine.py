#!/usr/bin/env python3
"""
Motor P.A.U. — piloto Espejo + Shopify Admin API + Qonto + Stripe (solo lectura).

Shopify (``api/shopify_bridge.py``):
  SHOPIFY_STORE_DOMAIN / SHOPIFY_MYSHOPIFY_HOST, SHOPIFY_SHOP_URL (alias),
  SHOPIFY_ADMIN_ACCESS_TOKEN o SHOPIFY_ACCESS_TOKEN, SHOPIFY_ADMIN_API_VERSION.

Qonto (``master_sync`` / ``force_qonto_collection``):
  QONTO_API_KEY o (QONTO_LOGIN + QONTO_SECRET_KEY), QONTO_BASE_URL,
  QONTO_BANK_IBAN o QONTO_IBAN.

Stripe (``stripe_fr_resolve`` — cuenta Paris / Connect):
  STRIPE_SECRET_KEY_FR (o STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY),
  STRIPE_CONNECT_ACCOUNT_ID_FR=acct_… opcional (balance en cuenta conectada).
  El piloto no crea cargos ni payouts; solo Balance.retrieve y Payout.list.

Sin credenciales: cada módulo se omite sin error fatal.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent
_API = _ROOT / "api"
for _p in (_API, _ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for name in (".env.production", ".env"):
        p = _ROOT / name
        if p.is_file():
            load_dotenv(p, override=False)


def _sync_shopify_env_aliases() -> None:
    """Alias habituales del búnker para que ``shopify_bridge`` resuelva sin fricción."""
    shop = (os.environ.get("SHOPIFY_SHOP_URL") or "").strip().replace("https://", "").replace("http://", "").split("/")[0]
    if shop and not (os.environ.get("SHOPIFY_STORE_DOMAIN") or "").strip():
        os.environ["SHOPIFY_STORE_DOMAIN"] = shop
    tok = (os.environ.get("SHOPIFY_ACCESS_TOKEN") or "").strip()
    if tok and not (os.environ.get("SHOPIFY_ADMIN_ACCESS_TOKEN") or "").strip():
        os.environ["SHOPIFY_ADMIN_ACCESS_TOKEN"] = tok


def _lead_id_from_silhouette(silhouette_id: str, extra: str = "") -> int:
    h = hashlib.sha256(f"{silhouette_id}|{extra}".encode("utf-8")).hexdigest()[:12]
    return int(h, 16) % 9_999_991 + 1


def _qonto_base_url() -> str:
    return (os.environ.get("QONTO_BASE_URL") or "https://thirdparty.qonto.com").rstrip("/")


def _qonto_auth_value() -> str:
    single = (os.environ.get("QONTO_API_KEY") or os.environ.get("QONTO_AUTHORIZATION_KEY") or "").strip()
    if single:
        return single
    login = (os.environ.get("QONTO_LOGIN") or "").strip()
    secret = (os.environ.get("QONTO_SECRET_KEY") or "").strip()
    if login and secret:
        return f"{login}:{secret}"
    return ""


def _http_get_json(url: str, headers: dict[str, str]) -> dict[str, Any] | None:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            return data if isinstance(data, dict) else None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        return None


def fetch_qonto_organization() -> dict[str, Any] | None:
    auth = _qonto_auth_value()
    if not auth:
        return None
    url = f"{_qonto_base_url()}/v2/organization"
    return _http_get_json(url, {"Authorization": auth, "Accept": "application/json"})


def _qonto_preferred_iban() -> str | None:
    raw = (os.environ.get("QONTO_BANK_IBAN") or os.environ.get("QONTO_IBAN") or "").strip()
    return raw or None


def _qonto_eur_accounts_summary(org_json: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    """Suma balance_cents EUR; respeta filtro IBAN si está definido (misma lógica que force_qonto)."""
    org_block = org_json.get("organization")
    accounts: list[Any] = []
    if isinstance(org_block, dict) and isinstance(org_block.get("bank_accounts"), list):
        accounts.extend(org_block["bank_accounts"])
    if isinstance(org_json.get("bank_accounts"), list):
        accounts.extend(org_json["bank_accounts"])
    iban_norm = (_qonto_preferred_iban() or "").replace(" ", "").upper()
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
        details.append(
            {
                "id": acc.get("id"),
                "iban_tail": (iban or "")[-4:] if iban else "",
                "balance_cents": c,
                "name": str(acc.get("name") or "")[:60],
            }
        )
    return total, details


def _qonto_first_eur_bank_account_id(org_json: dict[str, Any]) -> str | None:
    total, details = _qonto_eur_accounts_summary(org_json)
    _ = total
    for d in details:
        bid = d.get("id")
        if bid:
            return str(bid).strip()
    return None


def fetch_qonto_recent_credits(bank_account_id: str, *, per_page: int = 8) -> list[dict[str, Any]]:
    auth = _qonto_auth_value()
    if not auth or not bank_account_id:
        return []
    q = urllib.parse.urlencode(
        [
            ("bank_account_id", bank_account_id),
            ("per_page", str(max(1, min(per_page, 100)))),
            ("page", "1"),
            ("status[]", "completed"),
            ("side", "credit"),
        ]
    )
    url = f"{_qonto_base_url()}/v2/transactions?{q}"
    data = _http_get_json(url, {"Authorization": auth, "Accept": "application/json"})
    if not data:
        return []
    txs = data.get("transactions")
    if not isinstance(txs, list):
        return []
    slim: list[dict[str, Any]] = []
    for tx in txs[:per_page]:
        if not isinstance(tx, dict):
            continue
        slim.append(
            {
                "id": tx.get("id"),
                "amount_cents": tx.get("amount_cents"),
                "label": str(tx.get("label") or "")[:80],
                "side": tx.get("side"),
                "status": tx.get("status"),
            }
        )
    return slim


def _pilot_bridge_log_path() -> Path:
    return _ROOT / "logs" / "pau_pilot_bridge.jsonl"


def log_pilot_bridge_event(event: str, payload: dict[str, Any]) -> None:
    path = _pilot_bridge_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event": event,
            **payload,
        },
        ensure_ascii=False,
    )
    path.open("a", encoding="utf-8").write(line + "\n")


def _stripe_sum_for_currency(entries: Any, currency: str) -> int:
    cur = currency.lower()
    total = 0
    if not entries:
        return 0
    for e in entries:
        if isinstance(e, dict):
            c = str(e.get("currency") or "").lower()
            if c != cur:
                continue
            try:
                total += int(e.get("amount") or 0)
            except (TypeError, ValueError):
                continue
        else:
            c = str(getattr(e, "currency", "") or "").lower()
            if c != cur:
                continue
            try:
                total += int(getattr(e, "amount", 0) or 0)
            except (TypeError, ValueError):
                continue
    return total


def fetch_stripe_treasury_snapshot(*, payout_list_limit: int = 5) -> dict[str, Any] | None:
    """
    Balance Stripe (plataforma o Connect) y últimos payouts — solo lectura.
    Requiere paquete ``stripe`` instalado y clave en entorno (ver ``stripe_fr_resolve``).
    """
    try:
        import stripe
        from stripe_fr_resolve import (
            resolve_stripe_connect_account_fr,
            resolve_stripe_secret_fr,
            stripe_api_call_kwargs,
        )
    except ImportError:
        return None

    sk = (resolve_stripe_secret_fr() or "").strip()
    if not sk:
        return None

    stripe.api_key = sk
    kw = stripe_api_call_kwargs()
    acct = str(resolve_stripe_connect_account_fr() or "").strip()
    scope = f"connect:{acct}" if acct.startswith("acct_") else "platform"

    try:
        bal = stripe.Balance.retrieve(**kw)
    except Exception as exc:
        return {"ok": False, "scope": scope, "error": str(exc)[:400]}

    available = getattr(bal, "available", None) or []
    pending = getattr(bal, "pending", None) or []
    livemode = bool(getattr(bal, "livemode", False))

    snap: dict[str, Any] = {
        "ok": True,
        "scope": scope,
        "livemode": livemode,
        "eur_available_cents": _stripe_sum_for_currency(available, "eur"),
        "eur_pending_cents": _stripe_sum_for_currency(pending, "eur"),
    }

    try:
        lim = max(0, min(int(payout_list_limit), 10))
        if lim > 0:
            po_list = stripe.Payout.list(limit=lim, **kw)
            data = getattr(po_list, "data", None) or []
            snap["recent_payouts"] = []
            for p in data:
                snap["recent_payouts"].append(
                    {
                        "id": getattr(p, "id", None),
                        "status": getattr(p, "status", None),
                        "amount": getattr(p, "amount", None),
                        "currency": getattr(p, "currency", None),
                        "arrival_date": getattr(p, "arrival_date", None),
                    }
                )
    except Exception as exc:
        snap["recent_payouts_error"] = str(exc)[:200]

    return snap


def format_stripe_treasury_human(snap: dict[str, Any] | None) -> str:
    if snap is None:
        return "[Stripe] (módulo stripe o clave no disponible — omitido)."
    if snap.get("ok") is False:
        return f"[Stripe] error: {snap.get('error', 'unknown')} ({snap.get('scope', '')})"
    eur_a = int(snap.get("eur_available_cents") or 0)
    eur_p = int(snap.get("eur_pending_cents") or 0)
    lm = "LIVE" if snap.get("livemode") else "TEST"
    lines = [
        f"[Stripe] {lm} · {snap.get('scope')} · "
        f"EUR disponible={eur_a/100:.2f} · pendiente={eur_p/100:.2f}",
    ]
    rps = snap.get("recent_payouts")
    if isinstance(rps, list) and rps:
        for rp in rps[:5]:
            pid = rp.get("id") or "?"
            st = rp.get("status") or "?"
            amt = rp.get("amount")
            cur = (rp.get("currency") or "eur").upper()
            lines.append(f"    payout {pid} · {st} · {amt} {cur}")
    err = snap.get("recent_payouts_error")
    if err:
        lines.append(f"    (listado payouts: {err})")
    return "\n".join(lines)


class PAUPilotEngine:
    def __init__(self, *, dry_run: bool = False) -> None:
        _load_dotenv()
        _sync_shopify_env_aliases()
        self.dry_run = dry_run
        self.shop_url = (
            (os.environ.get("SHOPIFY_STORE_DOMAIN") or os.environ.get("SHOPIFY_SHOP_URL") or "").strip()
            or "5se9be-rv.myshopify.com"
        )
        self.metrics: dict[str, int] = {"conversions": 0, "scans": 0, "draft_orders": 0, "stripe_pulses": 0}
        self._stripe_snapshot: dict[str, Any] | None = None
        self._qonto_org: dict[str, Any] | None = None
        print("\n--- MOTOR P.A.U. ACTIVADO: MODO REAL ---")
        print(f"[Shopify] tienda: {self.shop_url}")
        if self.dry_run:
            print("[Modo] DRY-RUN — no se crearán borradores de pedido en Shopify.")

        self._stripe_snapshot = fetch_stripe_treasury_snapshot()
        if self._stripe_snapshot is not None:
            print(format_stripe_treasury_human(self._stripe_snapshot))
            if self._stripe_snapshot.get("ok") is True:
                self.metrics["stripe_pulses"] += 1
            log_pilot_bridge_event("stripe_pulse", {"summary": self._stripe_snapshot})

        self._qonto_org = fetch_qonto_organization()
        if self._qonto_org is not None:
            org = self._qonto_org.get("organization") if isinstance(self._qonto_org.get("organization"), dict) else {}
            name = str(org.get("legal_name") or org.get("name") or "org OK")
            total_c, details = _qonto_eur_accounts_summary(self._qonto_org)
            print(f"[Qonto] {name[:80]} · EUR agregado (céntimos)={total_c} · cuentas={len(details)}")
            bid = _qonto_first_eur_bank_account_id(self._qonto_org)
            if bid:
                credits = fetch_qonto_recent_credits(bid, per_page=5)
                if credits:
                    print(f"[Qonto] últimos créditos (muestra): {len(credits)} mov.")
            log_pilot_bridge_event("qonto_pulse", {"legal_hint": name[:120], "eur_total_cents": total_c})
        elif _qonto_auth_value():
            print("[Qonto] credencial presente pero GET /v2/organization falló (red o clave).")

    def confirm_action(self, message: str, *, auto_yes: bool = False) -> bool:
        """Muro de seguridad: confirmación explícita antes de ejecutar."""
        print(f"\n[SISTEMA]: {message}")
        if auto_yes:
            print("(auto-sí por flag --yes)")
            return True
        confirmacion = input("¿Confirmas y autorizas la ejecución? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("\n[!] OPERACIÓN ABORTADA. ACCESO AL BÚNKER PROTEGIDO.")
            sys.exit(1)
        return True

    def scan_silhouette(self, user_data: dict) -> dict[str, Any]:
        """Escaneo biométrico (demo con latencia simulada; ``user_data`` para trazabilidad)."""
        print("\nIniciando escaneo biométrico…")
        time.sleep(0.6)
        self.metrics["scans"] += 1
        seed = json.dumps(user_data, sort_keys=True, ensure_ascii=False)[:200]
        sid = "SIL-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10].upper()
        return {"status": "success", "silhouette_id": sid, "context": user_data}

    def get_perfect_selection(self, silhouette_id: str) -> list[dict[str, Any]]:
        """Looks: inventario real Shopify (Admin) si hay token + host; si no, demo soberano."""
        from shopify_bridge import admin_fetch_product_line_candidates

        rows = admin_fetch_product_line_candidates(limit=8)
        if rows:
            for i, r in enumerate(rows, start=1):
                r["pilot_slot"] = i
            print(f"\n[Shopify] {len(rows)} artículos cargados desde Admin API (primera variante / producto).")
            return rows

        print("\n[Shopify] Sin lectura Admin (token/host). Modo sugerencias demo.")
        _ = silhouette_id
        return [
            {"pilot_slot": 1, "name": "Look Principal", "price": 1250.00, "variant_id": None},
            {"pilot_slot": 2, "name": "Combinación A", "price": 850.00, "variant_id": None},
            {"pilot_slot": 3, "name": "Combinación B", "price": 920.00, "variant_id": None},
            {"pilot_slot": 4, "name": "Accesorios", "price": 310.00, "variant_id": None},
            {"pilot_slot": 5, "name": "Calzado", "price": 540.00, "variant_id": None},
        ]

    def execute_action(
        self,
        action_type: str,
        item: dict[str, Any] | int | None = None,
        *,
        silhouette_id: str = "",
        fabric_note: str = "PAU-PILOT",
    ) -> str:
        """Cinco botones del piloto; ``MI_SELECCION_PERFECTA`` crea draft order real si hay ``variant_id``."""
        if action_type == "MI_SELECCION_PERFECTA":
            return self._action_mi_seleccion_perfecta(item, silhouette_id=silhouette_id, fabric_note=fabric_note)
        if action_type == "RESERVAR_PROBADOR":
            return self._action_reservar_probador(silhouette_id)
        if action_type in ("STRIPE_TESORERIA", "PULSO_STRIPE"):
            return self._action_stripe_treasury()
        actions = {
            "VER_COMBINACIONES": "Desplegando sugerencias restantes (Sovereign Fit; tallas clásicas ocultas).",
            "GUARDAR_SILUETA": "Silueta y contexto de sesión listos para cifrado almacenamiento (pipeline bunker).",
            "COMPARTIR_LOOK": "Look listo para compartir — narrativa Sovereign Fit, sin tokens de talla prohibidos.",
        }
        return actions.get(action_type, "Acción no reconocida")

    def _action_mi_seleccion_perfecta(
        self,
        item: dict[str, Any] | int | None,
        *,
        silhouette_id: str,
        fabric_note: str,
    ) -> str:
        from shopify_bridge import admin_draft_order_create

        variant_id: int | None = None
        label = ""
        if isinstance(item, dict):
            raw = item.get("variant_id")
            if raw is not None:
                try:
                    variant_id = int(raw)
                except (TypeError, ValueError):
                    variant_id = None
            label = str(item.get("name") or item.get("title") or "ítem")
        elif isinstance(item, int):
            label = f"slot-{item}"
            z = (os.environ.get("SHOPIFY_ZERO_SIZE_VARIANT_ID") or "").strip()
            if z.isdigit():
                variant_id = int(z)

        if variant_id is None:
            return (
                "MI_SELECCION_PERFECTA (demo): define Admin token + dominio myshopify y catálogo con variantes, "
                "o SHOPIFY_ZERO_SIZE_VARIANT_ID para forzar una variante."
            )

        if self.dry_run:
            return f"DRY-RUN: no se creó borrador — variante {variant_id} ({label}) lista para checkout."

        lead = _lead_id_from_silhouette(silhouette_id or "anon", fabric_note)
        note = f"{fabric_note} · {label}"[:118]
        created = admin_draft_order_create(lead, note, variant_id)
        if not created:
            return f"No se pudo crear draft order Shopify (variant {variant_id}). Revisa scopes write_draft_orders y token."
        self.metrics["conversions"] += 1
        self.metrics["draft_orders"] += 1
        inv = created.get("invoice_url") or ""
        did = created.get("draft_order_id")
        name = created.get("name") or ""
        if isinstance(inv, str) and inv.startswith("http"):
            msg = f"Borrador {name or did} — pago / POS: {inv}"
        else:
            msg = f"Borrador creado id={did} ({name}); invoice_url no disponible en respuesta (revisa API / permisos)."
        log_pilot_bridge_event(
            "shopify_draft_order",
            {
                "silhouette_id": silhouette_id,
                "draft_order_id": did,
                "invoice_url_prefix": (str(inv)[:48] + "…") if isinstance(inv, str) and len(str(inv)) > 48 else inv,
                "stripe_scope": (self._stripe_snapshot or {}).get("scope"),
                "qonto_eur_cents": _qonto_eur_accounts_summary(self._qonto_org)[0] if self._qonto_org else None,
            },
        )
        return msg

    def _action_stripe_treasury(self) -> str:
        """Refresco Balance + payouts (misma política que al arranque)."""
        self._stripe_snapshot = fetch_stripe_treasury_snapshot()
        if self._stripe_snapshot and self._stripe_snapshot.get("ok") is True:
            self.metrics["stripe_pulses"] += 1
        log_pilot_bridge_event("stripe_pulse_manual", {"summary": self._stripe_snapshot})
        return format_stripe_treasury_human(self._stripe_snapshot)

    def _action_reservar_probador(self, silhouette_id: str) -> str:
        """Reserva simbólica + payload estable para POS / Make (sin hardcodear URL de terceros)."""
        token = hashlib.sha256(f"probador|{silhouette_id}|{time.time_ns()}".encode()).hexdigest()[:20]
        payload = {"type": "RESERVAR_PROBADOR", "silhouette_id": silhouette_id, "token": token}
        print(f"[POS] payload JSON: {json.dumps(payload, ensure_ascii=False)}")
        return "Código de reserva generado (consola). Conecta webhook Make → POS Pro en despliegue."

    def snap_gesture_activation(self, brand_model_id: str) -> str:
        """Cambio de look instantáneo (Chasquido Balmain)."""
        print(f"\n[!] ACTIVANDO CHASQUIDO: Avatar → modelo {brand_model_id}.")
        return "Look visualizado correctamente."


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="P.A.U. piloto — Shopify + Qonto + Stripe (lectura) + CLI.")
    ap.add_argument("--dry-run", action="store_true", help="No crear draft orders (sí puede leer catálogo).")
    ap.add_argument("--yes", "-y", action="store_true", help="Saltar confirmación interactiva.")
    return ap.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        pau = PAUPilotEngine(dry_run=args.dry_run)

        pau.confirm_action(
            "Vas a iniciar una sesión de escaneo biométrico en el Espejo Digital.",
            auto_yes=args.yes,
        )

        scan = pau.scan_silhouette({"height": 175, "event": "Gala"})
        sid = str(scan.get("silhouette_id") or "SIL-UNKNOWN")

        if scan.get("status") == "success":
            looks = pau.get_perfect_selection(sid)
            pick = looks[0] if looks else {}
            resultado = pau.execute_action(
                "MI_SELECCION_PERFECTA",
                pick,
                silhouette_id=sid,
                fabric_note="PAU-PILOT-GALA",
            )
            print(f"\nEstado: {resultado}")
            print(pau.execute_action("VER_COMBINACIONES"))
            print(pau.execute_action("RESERVAR_PROBADOR", silhouette_id=sid))
            pau.snap_gesture_activation("LVMH-MARAIS-01")

        print("\n--- EJECUCIÓN COMPLETADA SIN ERRORES ---")
        print(f"[Métricas] {json.dumps(pau.metrics, ensure_ascii=False)}")

    except KeyboardInterrupt:
        print("\n[!] Interrumpido por el usuario.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR CRÍTICO]: {e}", file=sys.stderr)
        sys.exit(1)
