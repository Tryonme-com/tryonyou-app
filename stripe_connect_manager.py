"""
Stripe Connect Platform Manager — TryOnYou / Espejo Digital Soberano.

Gestiona cuentas Connect V2, onboarding y Destination Charges
para vendedores de la plataforma.

Bajo Protocolo de Soberanía V10 — Founder: Rubén Espinar Rodríguez
@CertezaAbsoluta @lo+erestu | Patente PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import stripe

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
BPI_DOSSIER_ID = os.getenv("BPI_DOSSIER_ID", "27-206446")

_test_mode = STRIPE_API_KEY.startswith("sk_test_")

stripe_client: Optional[stripe.StripeClient] = None
if STRIPE_API_KEY:
    stripe_client = stripe.StripeClient(STRIPE_API_KEY)


def _require_client() -> stripe.StripeClient:
    if stripe_client is None:
        raise RuntimeError(
            "STRIPE_SECRET_KEY no configurada. "
            "Define la variable de entorno antes de usar el manager."
        )
    return stripe_client


class TryOnYouManager:
    """Gestor de operaciones Stripe Connect para la plataforma TryOnYou."""

    def __init__(self, platform_fee_cents: int = 500):
        self.platform_fee_cents = platform_fee_cents

    def create_connected_account(self, email: str, name: str) -> str:
        """Crea una cuenta Stripe Connect V2 para un nuevo vendedor."""
        client = _require_client()
        try:
            account = client.v2.core.accounts.create(
                display_name=name,
                contact_email=email,
                identity={"country": "us"},
                dashboard="express",
                defaults={
                    "responsibilities": {
                        "fees_collector": "application",
                        "losses_collector": "application",
                    },
                },
                configuration={
                    "recipient": {
                        "capabilities": {
                            "stripe_balance": {
                                "stripe_transfers": {"requested": True},
                            },
                        },
                    },
                },
            )
            return account.id
        except Exception as e:
            raise RuntimeError(f"Error al crear cuenta Connect: {e}") from e

    def get_onboarding_link(self, account_id: str, return_url: str) -> str:
        """Genera el link de onboarding para que el vendedor complete su perfil."""
        client = _require_client()
        link = client.v2.core.account_links.create(
            account=account_id,
            use_case={
                "type": "account_onboarding",
                "account_onboarding": {
                    "configurations": ["recipient"],
                    "refresh_url": return_url,
                    "return_url": return_url,
                },
            },
        )
        return link.url

    def check_account_status(self, account_id: str) -> dict:
        """Verifica si la cuenta está lista para recibir transferencias."""
        client = _require_client()
        acc = client.v2.core.accounts.retrieve(
            account_id,
            params={"include": ["configuration.recipient", "requirements"]},
        )
        is_active = (
            acc.configuration.recipient.capabilities.stripe_balance.stripe_transfers.status
            == "active"
        )
        req_status = acc.requirements.summary.minimum_deadline.status
        is_onboarded = req_status not in ("currently_due", "past_due")

        return {
            "ready": is_active and is_onboarded,
            "transfers_active": is_active,
            "onboarded": is_onboarded,
            "status": "OPERATIVO" if is_active else "PENDIENTE",
        }

    def create_checkout_session(
        self,
        price_id: str,
        destination_account: str,
        success_url: str = "https://tryonyou.com/success",
        cancel_url: Optional[str] = None,
    ) -> str:
        """Crea una Checkout Session con Destination Charge y comisión de plataforma."""
        client = _require_client()
        params: dict = {
            "line_items": [{"price": price_id, "quantity": 1}],
            "payment_intent_data": {
                "application_fee_amount": self.platform_fee_cents,
                "transfer_data": {"destination": destination_account},
            },
            "mode": "payment",
            "success_url": success_url,
        }
        if cancel_url:
            params["cancel_url"] = cancel_url
        session = client.checkout.sessions.create(**params)
        return session.url


class TryOnYouOrchestrator:
    """Orquestador de operaciones financieras: Lafayette + Bpifrance + Stripe V2 events."""

    DEFAULT_RELIC_ASSETS = 65_000
    DEFAULT_CASH_ON_HAND = 32_800
    DEFAULT_LAFAYETTE_CONTRACT_EUR = 88_000
    LAFAYETTE_FEE_PERCENT = 5

    def __init__(
        self,
        relic_assets: Optional[int] = None,
        cash_on_hand: Optional[int] = None,
        lafayette_contract_eur: Optional[int] = None,
    ):
        self.relic_assets = (
            self.DEFAULT_RELIC_ASSETS if relic_assets is None else relic_assets
        )
        self.cash_on_hand = (
            self.DEFAULT_CASH_ON_HAND if cash_on_hand is None else cash_on_hand
        )
        self.lafayette_contract_eur = (
            self.DEFAULT_LAFAYETTE_CONTRACT_EUR
            if lafayette_contract_eur is None
            else lafayette_contract_eur
        )

    def generate_bpi_report(self) -> dict:
        """Genera un resumen de solvencia para Bpifrance."""
        total = self.relic_assets + self.cash_on_hand + self.lafayette_contract_eur
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "dossier_bpi": BPI_DOSSIER_ID,
            "relic_assets_eur": self.relic_assets,
            "cash_on_hand_eur": self.cash_on_hand,
            "lafayette_contract_eur": self.lafayette_contract_eur,
            "total_assets_eur": total,
            "status": "SOLVENTE",
        }

    def create_lafayette_checkout(
        self,
        destination_account: str,
        success_url: str = "https://tryonyou.com/success",
        cancel_url: Optional[str] = None,
    ) -> str:
        """Checkout Session para el cobro Lafayette (Pack Empire) con Destination Charge."""
        client = _require_client()
        fee_cents = int(
            self.lafayette_contract_eur * 100 * self.LAFAYETTE_FEE_PERCENT / 100
        )
        params: dict = {
            "line_items": [
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Pack Empire - Jules AI (Lafayette)",
                        },
                        "unit_amount": self.lafayette_contract_eur * 100,
                    },
                    "quantity": 1,
                }
            ],
            "payment_intent_data": {
                "application_fee_amount": fee_cents,
                "transfer_data": {"destination": destination_account},
            },
            "mode": "payment",
            "success_url": success_url,
        }
        if cancel_url:
            params["cancel_url"] = cancel_url
        session = client.checkout.sessions.create(**params)
        return session.url

    def prepare_bpi_evidence(
        self,
        days: int = 90,
        limit: int = 100,
        output_path: Optional[str] = None,
    ) -> dict:
        """Genera un JSON de evidencia con los pagos exitosos de Stripe para Bpifrance.

        Consulta PaymentIntents con status ``succeeded`` de los últimos *days* días,
        extrae la información relevante (importe, moneda, fecha, comisión de plataforma,
        destino Connect) y construye un dossier listo para adjuntar al expediente BPI.

        Args:
            days: Ventana temporal hacia atrás (por defecto 90 días).
            limit: Máximo de registros por página de la API (100 máx Stripe).
            output_path: Si se indica, escribe el JSON a disco.

        Returns:
            dict con la estructura completa de evidencia.
        """
        client = _require_client()

        now = datetime.now(timezone.utc)
        since = now - timedelta(days=days)
        created_gte = int(since.timestamp())

        transactions: list[dict] = []
        total_revenue_cents = 0
        total_fees_cents = 0
        currency_set: set[str] = set()

        has_more = True
        starting_after: Optional[str] = None

        while has_more:
            params: dict = {
                "limit": min(limit, 100),
                "created": {"gte": created_gte},
            }
            if starting_after:
                params["starting_after"] = starting_after

            page = client.payment_intents.list(**params)

            for pi in page.data:
                if pi.status != "succeeded":
                    continue

                fee_amount = 0
                if hasattr(pi, "application_fee_amount") and pi.application_fee_amount:
                    fee_amount = pi.application_fee_amount

                destination = None
                if hasattr(pi, "transfer_data") and pi.transfer_data:
                    destination = getattr(pi.transfer_data, "destination", None)

                tx = {
                    "payment_intent_id": pi.id,
                    "amount_cents": pi.amount,
                    "currency": pi.currency,
                    "created": datetime.fromtimestamp(
                        pi.created, tz=timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "description": pi.description or "",
                    "platform_fee_cents": fee_amount,
                    "destination_account": destination,
                }
                transactions.append(tx)
                total_revenue_cents += pi.amount
                total_fees_cents += fee_amount
                currency_set.add(pi.currency)

            has_more = page.has_more
            if has_more and page.data:
                starting_after = page.data[-1].id

        primary_currency = "eur"
        if currency_set:
            primary_currency = "eur" if "eur" in currency_set else next(iter(currency_set))

        solvency = self.generate_bpi_report()

        evidence = {
            "meta": {
                "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "dossier_bpi": BPI_DOSSIER_ID,
                "period_days": days,
                "period_from": since.strftime("%Y-%m-%d"),
                "period_to": now.strftime("%Y-%m-%d"),
                "stripe_mode": "TEST" if _test_mode else "LIVE",
            },
            "summary": {
                "total_succeeded_transactions": len(transactions),
                "total_revenue_cents": total_revenue_cents,
                "total_revenue_display": f"{total_revenue_cents / 100:.2f} {primary_currency.upper()}",
                "total_platform_fees_cents": total_fees_cents,
                "total_platform_fees_display": f"{total_fees_cents / 100:.2f} {primary_currency.upper()}",
                "currencies": sorted(currency_set),
            },
            "solvency_snapshot": solvency,
            "transactions": transactions,
        }

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(evidence, f, ensure_ascii=False, indent=2)

        return evidence

    @staticmethod
    def handle_v2_thin_event(event_id: str) -> dict:
        """Recupera y procesa un Thin Event de la API V2."""
        client = _require_client()
        event = client.v2.core.events.retrieve(event_id)
        result: dict = {"event_id": event_id, "type": event.type}

        if event.type == "v2.core.account[requirements].updated":
            result["action"] = "requirements_updated"
            result["account_id"] = getattr(
                getattr(event, "data", None), "object", {}
            )
            if hasattr(result["account_id"], "id"):
                result["account_id"] = result["account_id"].id

        return result


if __name__ == "__main__":
    if _test_mode:
        print("OPERANDO EN MODO TEST")

    manager = TryOnYouManager()
    orchestrator = TryOnYouOrchestrator()
    report = orchestrator.generate_bpi_report()
    print(f"Reporte Bpifrance: {report}")
    print("Stripe Connect Manager + Orchestrator listo para procesar pagos.")
