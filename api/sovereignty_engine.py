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
        # Configuración principal de deuda de grupo.
        self.nodes = ["Haussmann", "Marais"]
        self.expiration_date = dt.date(2026, 4, 22)
        self.base_debt = 475_400.00
        self.discount_rate = 0.15
        self.tva_rate = 1.20

    def calculate_current_threshold(self, today: dt.date | None = None) -> tuple[float, str]:
        """Calcula umbral de desbloqueo TTC según fecha de referencia."""
        current_day = today or dt.date.today()
        if current_day <= self.expiration_date:
            net_amount = self.base_debt * (1 - self.discount_rate)
            status = "OFERTA_ACTIVA_15%"
        else:
            net_amount = self.base_debt
            status = "TARIFA_ESTÁNDAR_VENCIDA"
        return round(net_amount * self.tva_rate, 2), status

    def deploy_kill_switch(self, today: dt.date | None = None) -> dict:
        """Construye payload de bloqueo financiero global."""
        threshold, status = self.calculate_current_threshold(today=today)
        return {
            "status": "LOCKED",
            "message": "RÉSEAU SUSPENDU : LIQUIDATION DE GROUPE EN ATTENTE",
            "required_amount": f"{threshold:.2f} € TTC",
            "required_amount_eur": threshold,
            "reason": f"Défaut de paiement constaté - {status}",
            "deadline": self.expiration_date.strftime("%d/%m/%Y"),
            "nodes": self.nodes,
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
