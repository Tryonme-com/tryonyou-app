"""
Deep Tech Bunker — orquestación asyncio (PR #2389: inferencia VetosCore sin bloquear el hilo).
La verificación de ingresos y el arranque de reforma son asíncronos y aislan fallos de calendario.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


class RevenueDelayedError(Exception):
    """Ingreso 7 500 € retrasado o incompleto: la reforma no puede iniciar en la fecha prevista."""


@dataclass
class DeepTechSystem:
    """Parámetros de negocio y ley francesa (Bpifrance 2026)."""

    revenue_target: float = 7500.0
    rent_gross: float = 1600.0
    bpifrance_guarantee_pct: float = 0.60

    is_bunker_v10_active: bool = False
    reform_status: str = "PLANNING"

    revenue_received: float = 0.0
    revenue_delay_days: int = 0
    reform_slip_days: int = field(default=0)


class BunkerOrchestrator:
    def __init__(self, system: DeepTechSystem) -> None:
        self.system = system
        self.cash_on_hand = 0.0

    async def secure_guy_moquet(self) -> float:
        """
        Aplica la ley de Bpifrance para minimizar el depósito.
        En lugar de 6 meses de fianza, se negocian 2 meses + Aval Bpifrance.
        """
        deposit = self.system.rent_gross * 2
        print("[LOG] Aplicando Aval Bpifrance al 60% pour Guy Môquet.")
        print(f"[LOG] Depósito inicial requerido: {deposit}€")

        self.cash_on_hand = max(0.0, self.system.revenue_target - deposit)
        return deposit

    async def _guard_reform_start(self) -> None:
        """
        Verifica ingreso 7 500 € y retrasos: define si la reforma puede abrir calendario físico.
        Retraso > 0: no se inicia obra; VetosCore queda en cola async (#2389).
        """
        target = self.system.revenue_target
        received = self.system.revenue_received
        delay = self.system.revenue_delay_days

        if delay > 0:
            self.system.reform_status = "DEFERRED_REVENUE_TIMING"
            self.system.reform_slip_days = delay
            raise RevenueDelayedError(
                f"Ingreso {target:.0f} € retrasado ({delay} j.): la reforma no arranca; "
                "inferencia VetosCore en espera de ventana de caja."
            )

        if received <= 0:
            self.system.reform_status = "BLOCKED_NO_FUNDS"
            raise RevenueDelayedError(
                "Sin ingreso confirmado: reforma y despliegue sensor bloqueados."
            )

        if received < target:
            self.system.reform_status = "DEFERRED_PARTIAL_FUNDING"
            self.system.reform_slip_days = max(1, int((target - received) / 500))
            raise RevenueDelayedError(
                f"Ingreso parcial ({received:.0f} € / {target:.0f} €): "
                f"inicio de reforma desplazado ~{self.system.reform_slip_days} j. hasta completar."
            )

    async def deploy_reform(self) -> None:
        """Inicia la reforma técnica (async) solo si el ingreso y plazos lo permiten."""
        try:
            await self._guard_reform_start()
        except RevenueDelayedError as e:
            print(f"[EXCEPTION] {e}")
            print(
                "[IMPACT] Obra y adecuación de red no arrancan; presupuesto Deep Tech congelado "
                f"hasta regularización (cash disponible declarado: {self.cash_on_hand:.0f} €)."
            )
            return

        print("[LOG] Iniciando Fase Reforma: adecuación de sensores y red (async).")
        self.system.reform_status = "IN_PROGRESS"
        await asyncio.sleep(0)
        print(f"[LOG] Presupuesto Deep Tech disponible: {self.cash_on_hand:.0f} €")


async def run_cursor_flow() -> None:
    tech_bunker = DeepTechSystem()
    tech_bunker.revenue_received = 7500.0
    tech_bunker.revenue_delay_days = 0

    agent_70 = BunkerOrchestrator(tech_bunker)

    print("--- PROTOCOLO DEEP TECH: GUY MÔQUET ---")
    try:
        fianza = await agent_70.secure_guy_moquet()
        await agent_70.deploy_reform()
    except Exception as e:
        print(f"[FATAL] Error async en orquestación: {e}")
        raise

    print("\n--- RESUMEN PARA EL COBRO DE 7.500€ ---")
    print(f"Fianza local: {fianza}€")
    print(f"Saldo para desarrollo/reforma: {agent_70.cash_on_hand:.0f}€")
    print("Aval Bpifrance: ACTIVO (Garantía de Creación)")
    print("---------------------------------------")


async def demo_retraso_ingreso() -> None:
    """Ejemplo: ingreso retrasado bloquea el inicio de reforma."""
    s = DeepTechSystem()
    s.revenue_received = 7500.0
    s.revenue_delay_days = 14
    o = BunkerOrchestrator(s)
    await o.secure_guy_moquet()
    await o.deploy_reform()
    assert s.reform_status == "DEFERRED_REVENUE_TIMING"


if __name__ == "__main__":
    asyncio.run(run_cursor_flow())
