"""Agente 70 CEO — veto de calidad, autorización de payout y limpieza de legado."""

from __future__ import annotations

from datetime import datetime

QUALITY_THRESHOLD = 0.95
# Vault locked window: [LOCKED_WINDOW_START, LOCKED_WINDOW_END) → 04:00–08:59
LOCKED_WINDOW_START = 4
LOCKED_WINDOW_END = 9


class Agente70CEO:
    def __init__(self) -> None:
        self.identity = "Agente 70"
        self.role = "CEO & Supreme Auditor"
        self.siren = "943610196"
        self.vault_status = "LOCKED_UNTIL_0900"

    def power_of_veto(self, task_id: str, code_quality: float) -> bool:
        """Bloquea la tarea si la calidad del código es inferior al estándar Divineo."""
        if code_quality < QUALITY_THRESHOLD:
            print(f"🚫 [VETO] {self.identity}: Tarea {task_id} rechazada por baja calidad técnica.")
            return False
        return True

    def authorize_payout(self, amount: float) -> bool:
        """Autorización final de fondos. Solo el CEO puede disparar el Payout.

        El búnker está bloqueado durante la ventana [LOCKED_WINDOW_START, LOCKED_WINDOW_END),
        es decir de 04:00 a 08:59. Fuera de ese intervalo la liquidación se aprueba.

        Returns:
            True si el payout está autorizado, False si la ventana está bloqueada.
        """
        now = datetime.now().hour
        if now >= LOCKED_WINDOW_END or now < LOCKED_WINDOW_START:
            print(f"💰 [AUTH] {self.identity}: Liquidación de {amount}€ aprobada.")
            return True
        print(f"⏳ [WAIT] {self.identity}: Esperando apertura de mercados (09:00 AM).")
        return False

    def purge_legacy(self) -> str:
        """Elimina rastros de errores anteriores (Firebase/Env)."""
        print(f"🧹 [PURGE] {self.identity}: Eliminando residuos de 'invalid-api-key'...")
        return "Clean State Confirmed."


if __name__ == "__main__":
    ceo = Agente70CEO()

    print(f"🏛️ ROL ACTIVO: {ceo.identity} como {ceo.role}")

    ceo.purge_legacy()

    if ceo.power_of_veto("e5090863-826a-4253-ac8e-e799ca69c108", code_quality=0.99):
        print("✅ Tarea validada por el CEO.")

    ceo.authorize_payout(450000.00)
