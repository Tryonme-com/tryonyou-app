from __future__ import annotations

import os


class ContractSovereignty:
    """Comprobaciones genéricas de activación (sin deudas ficticias precargadas)."""

    def __init__(self) -> None:
        self.required_activation_eur = float(os.getenv("CONTRACT_ACTIVATION_AMOUNT_EUR") or "0")

    def check_activation_requirements(self) -> str | None:
        if self.required_activation_eur <= 0:
            return (
                "Sin CONTRACT_ACTIVATION_AMOUNT_EUR configurado. "
                "Define el importe tras contrato firmado."
            )
        return None


if __name__ == "__main__":
    sovereign = ContractSovereignty()
    msg = sovereign.check_activation_requirements()
    print(msg or "OK: umbral de activación configurado en entorno.")
