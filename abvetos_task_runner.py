"""AbvetosTaskRunner — sincronización de tareas y validación de integridad Firebase.

SIREN: 943610196
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

TASK_ID = "1b0d7405-aff9-465a-b680-92133b499ba8"
SIREN = "943610196"


class AbvetosTaskRunner:
    def __init__(self) -> None:
        self.task_id = TASK_ID
        self.siren = SIREN
        self.api_url = (
            "https://api.github.com/repos/Tryonme-com/"
            f"TRYONME-TRYONYOU-ABVETOS--INTELLIGENCE--SYSTEM/tasks/{self.task_id}"
        )

    def verify_firebase_integrity(self) -> str:
        """Comprueba que la API Key no sea nula y tenga el formato correcto."""
        api_key = os.getenv("VITE_FIREBASE_API_KEY") or os.getenv("FIREBASE_API_KEY")

        if not api_key:
            return "❌ ERROR: API Key ausente en el entorno local."

        if not api_key.startswith("AIza"):
            return "❌ ERROR: Formato de Firebase API Key inválido (Debe empezar por AIza)."

        return "✅ INTEGRIDAD DE KEY: Validada."

    def sync_task_status(self) -> None:
        """Marca la tarea como 'In Progress' en el sistema ABVETOS."""
        print(f"📡 Sincronizando tarea {self.task_id}...")
        status = self.verify_firebase_integrity()
        print(status)

        if "✅" in status:
            print("🚀 Tarea lista para SUPERCOMMIT. Destino: Payout 09:00 AM.")
        else:
            print("⚠️ Bloqueo detectado. Corrige el .env antes de continuar.")


if __name__ == "__main__":
    runner = AbvetosTaskRunner()
    runner.sync_task_status()
