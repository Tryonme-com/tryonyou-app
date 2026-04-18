"""
EntryPoint Golden Peacock — orquestación autónoma tryonyou.app (Agente70 + Abvetos).
"""

from abvetos_connector import AbvetosApp
from agente_core import Agente70


class SistemaAutonomo:
    """
    Controlador centralizado para la ejecución autónoma de tryonyou.app.
    Cursor debe tratar esta clase como el punto de entrada principal (EntryPoint).
    """

    def __init__(self) -> None:
        self.agente = Agente70()
        self.app = AbvetosApp()

    def inicializar_todo(self) -> None:
        """
        Cursor: ejecutar al arrancar el servidor (backend).

        1. Inicia el hilo de vigilancia 402 (liquidez / FinancialGuard).
        2. Listeners del DOM: en el cliente (React/Vite); aquí no aplica.
        3. Valida la conexión con Divineo_Leads_DB (env DIVINEO_LEADS_DB_PATH / LEADS_DB_PATH).
        """
        print("--- Iniciando Protocolo Golden Peacock ---")
        self.agente.validar_divineo_leads_db()
        self.agente.start_autonomous_cycle()
        print("Agente 70: Vigilancia activa. Estado: OPERATIONAL.")

    def ejecutar_flujo_usuario(self, user_id: str, message: str):
        """Cursor: gestiona toda la interacción entrante (Make.com / chat vía AbvetosApp)."""
        return self.app.handle_request(user_id, message)


if __name__ == "__main__":
    sistema = SistemaAutonomo()
    sistema.inicializar_todo()
