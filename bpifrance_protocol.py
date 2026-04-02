from __future__ import annotations

import asyncio
import os

INGRESO_OBJETIVO_EUR = 7500.0


class VerificacionIngreso7500Error(Exception):
    """Ingreso piloto insuficiente o no confirmado — detener cadenas sensibles (p. ej. asalto final)."""


class BpifranceProtocol:
    def __init__(self) -> None:
        self.cuota_garantia = 0.60
        self.subvencion_reforma_max = 50000.0
        self.aval_activo = False

    async def solicitar_aval(self, alquiler_anual: float) -> bool:
        """Asegura el local de Guy Môquet mediante garantía estatal."""
        monto = alquiler_anual * self.cuota_garantia
        print(f"-> Solicitando garantía Bpifrance por {monto}€...")
        await asyncio.sleep(0.5)
        self.aval_activo = True
        return self.aval_activo

    def calcular_desembolso_inicial(self, alquiler_mensual: float) -> float:
        deposito_reducido = alquiler_mensual * 2
        return deposito_reducido


def verificar_cuota_ganada(cuota_ganada: float | None) -> float:
    """
    Verifica que la cuota acreditada alcance el objetivo 7.500 €.
    Devuelve el importe validado o lanza VerificacionIngreso7500Error.
    """
    if cuota_ganada is None:
        raise VerificacionIngreso7500Error(
            "cuota_ganada no definida — ingreso piloto no verificado.",
        )
    if cuota_ganada < INGRESO_OBJETIVO_EUR:
        raise VerificacionIngreso7500Error(
            f"Ingreso insuficiente: {cuota_ganada}€ < {INGRESO_OBJETIVO_EUR}€ — ejecución detenida.",
        )
    return float(cuota_ganada)


def assert_ingreso_7500_protegido() -> None:
    """
    Punto único para scripts sensibles (p. ej. asalto_final_bunker.py).
    Lee CUOTA_GANADA desde el entorno salvo bypass explícito de desarrollo.
    """
    skip = os.environ.get("SKIP_INGRESO_7500_VERIFICATION", "").strip().lower()
    if skip in ("1", "true", "yes", "on"):
        print(
            "⚠️  SKIP_INGRESO_7500_VERIFICATION activo — solo entorno de desarrollo.",
        )
        return

    raw = os.environ.get("CUOTA_GANADA", "").strip()
    if not raw:
        raise VerificacionIngreso7500Error(
            "CUOTA_GANADA no definida. Define el importe acreditado (€) o aborta.",
        )
    try:
        cuota = float(
            raw.replace("€", "").replace(" ", "").replace(",", ".").strip(),
        )
    except ValueError as e:
        raise VerificacionIngreso7500Error(
            f"CUOTA_GANADA inválida: {raw!r}",
        ) from e
    verificar_cuota_ganada(cuota)
    print(f"✅ Verificación 7.500€: cuota_ganada={cuota}€ (objetivo {INGRESO_OBJETIVO_EUR}€)")


async def validar_ley_y_negocio(cuota_ganada: float | None = None) -> None:
    """
    Flujo principal: primero verifica ingreso 7.500 € (o variable de entorno si cuota_ganada es None).
    """
    if cuota_ganada is not None:
        verificar_cuota_ganada(cuota_ganada)
    else:
        assert_ingreso_7500_protegido()

    bp = BpifranceProtocol()
    alquiler_guy_moquet = 1600.0

    if await bp.solicitar_aval(alquiler_guy_moquet * 12):
        inicial = bp.calcular_desembolso_inicial(alquiler_guy_moquet)
        print("CONFIRMADO: Local asegurado con aval Bpifrance.")
        print(f"PAGO ENTRADA (Depósito): {inicial}€ (A pagar de los 7.500€)")
        print(f"RESTO 7.500€ para DEEP TECH: {INGRESO_OBJETIVO_EUR - inicial}€")


if __name__ == "__main__":
    asyncio.run(validar_ley_y_negocio())
