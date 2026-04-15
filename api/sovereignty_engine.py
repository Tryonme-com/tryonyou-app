"""
Sovereignty Engine — payment threshold guard for V11 endpoints.

Aplica un cierre financiero global (HTTP 402) cuando el balance operativo
Qonto queda por debajo del umbral de desbloqueo calculado.
"""

from __future__ import annotations

import datetime as dt
import os

from treasury_monitor import get_treasury_status


class SovereigntyEngine:
    def __init__(self) -> None:
        # Configuración de críticos (Lafayette + LVMH Marais).
        self.client_group = "Lafayette-LVMH-Marais"
        self.targets = ["Galeries Lafayette Haussmann", "Marais LVMH"]
        self.deadline_discount = dt.date(2026, 4, 22)

        # Matemáticas HT de soberanía.
        self.debt_haussmann = 210_300.00
        self.setup_marais = 27_500.00
        self.annual_licence_group = 118_800.00 + 118_800.00
        self.base_total_ht = (
            self.debt_haussmann
            + self.setup_marais
            + self.annual_licence_group
        )
        self.discount_rate = 0.15
        self.tva_rate = 1.20

    def calculate_current_threshold(self, today: dt.date | None = None) -> tuple[float, str]:
        """Calcula umbral de desbloqueo TTC según fecha de referencia."""
        current_day = today or dt.date.today()
        if current_day <= self.deadline_discount:
            final_ht = self.base_total_ht * (1 - self.discount_rate)
            status = "OFFRE_FLASH_ACTIVE_15"
        else:
            final_ht = self.base_total_ht
            status = "TARIF_STANDARD_PENALITÉ"
        return round(final_ht * self.tva_rate, 2), status

    def deploy_kill_switch(self, today: dt.date | None = None) -> dict:
        """Construye payload de bloqueo financiero global."""
        threshold, status = self.calculate_current_threshold(today=today)
        return {
            "ACTION": "LOCKDOWN_TOTAL",
            "TARGETS": self.targets,
            "REQUIRED_DEPOSIT": f"{threshold:.2f} € TTC",
            "UI_RENDER": "BLACK_SCREEN_ULTIMATUM",
            "REASON": f"Audit de liquidation en cours - {status}",
            "CONTACT": "TRYONYOU_ADMIN_SOPORTE",
            "status": "LOCKED",
            "message": "RÉSEAU SUSPENDU : LIQUIDATION DE GROUPE EN ATTENTE",
            "required_amount": f"{threshold:.2f} € TTC",
            "required_amount_eur": threshold,
            "reason": f"Défaut de paiement constaté - {status}",
            "deadline": self.deadline_discount.strftime("%d/%m/%Y"),
            "nodes": ["Haussmann", "Marais"],
            "client_group": self.client_group,
        }


def _read_qonto_balance_eur() -> float:
    raw = (os.getenv("QONTO_BALANCE_EUR") or "").strip()
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    treasury = get_treasury_status()
    return float(treasury.get("reserve_eur", 0.0))


def v11_payment_required_guard() -> tuple[dict, int] | None:
    """
    Si balance < umbral, devuelve payload de bloqueo + 402.
    Si no, devuelve None.
    """
    engine = SovereigntyEngine()
    threshold, status = engine.calculate_current_threshold()
    balance = _read_qonto_balance_eur()
    if balance >= threshold:
        return None

    payload = engine.deploy_kill_switch()
    payload.update(
        {
            "http_status": 402,
            "payment_status": "PAYMENT_REQUIRED",
            "qonto_balance_eur": round(balance, 2),
            "threshold_status": status,
        }
    )
    return payload, 402
