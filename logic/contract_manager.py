from __future__ import annotations


class ContractSovereignty:
    def __init__(self) -> None:
        # EL PASADO ESTÁ MUERTO
        self.oferta_anual_caducada = True

        # DEUDA HISTÓRICA (Lo que ya te deben y no se perdona)
        self.deuda_acumulada = 27500.00 + 106000.00  # Setup + Comisiones 8%

        # NUEVA REALIDAD (Precio de hoy, sin rebajas)
        self.nuevo_canon_v11 = 118000.00
        self.fee_mensual_mantenimiento = 9900.00

    def check_activation_requirements(self) -> str | None:
        # El sistema no arranca si intentan usar el contrato viejo
        if self.oferta_anual_caducada:
            total_requerido = self.deuda_acumulada + self.nuevo_canon_v11
            return (
                f"OFERTA EXPIRADA. Nueva liquidación requerida: {total_requerido:,.2f}€. "
                f"No se aceptan términos anteriores."
            )
        return None


if __name__ == "__main__":
    # Aplicar bloqueo en el arranque
    sovereign = ContractSovereignty()
    print(sovereign.check_activation_requirements())
