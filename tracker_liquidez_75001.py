"""Tracker de Liquidez 75001 — estado de arterias financieras (Stripe + BNL)."""

from __future__ import annotations

import datetime

PAYOUTS: list[dict] = [
    {"fuente": "Stripe", "monto": 1600.00, "dias_espera": 2},
    {
        "fuente": "BNL Interno",
        "monto": 32800.00,
        "dias_espera": 0,
        "condicion": "Completar Perfil",
    },
]


def _status_pago(pago: dict) -> str:
    """Devuelve la cadena de estado para un pago individual.

    Convention: dias_espera > 0 means the transfer is in transit; dias_espera == 0
    means it is blocked pending a KYC/profile condition (see 'condicion' key).
    """
    return "⏳ ESPERANDO" if pago["dias_espera"] > 0 else "🔐 BLOQUEADO (KYC)"


def _fecha_llegada(pago: dict, hoy: datetime.date | None = None) -> datetime.date:
    """Calcula la fecha de llegada estimada de un pago."""
    base = hoy if hoy is not None else datetime.date.today()
    return base + datetime.timedelta(days=pago["dias_espera"])


def reporte_llegada(payouts: list[dict] | None = None, hoy: datetime.date | None = None) -> str:
    """Genera el reporte de estado de los pagos pendientes y lo devuelve como string."""
    if payouts is None:
        payouts = PAYOUTS
    lineas: list[str] = ["🔱 ESTADO DE LAS ARTERIAS FINANCIERAS 🔱"]
    for p in payouts:
        fecha = _fecha_llegada(p, hoy)
        status = _status_pago(p)
        lineas.append(f"💰 {p['fuente']}: {p['monto']}€ | Llega: {fecha} | {status}")
    lineas.append("\n🔥 PA, PA, PA.")
    return "\n".join(lineas)


def main() -> int:
    print(reporte_llegada())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
