"""
AbvetosTaskRunner — verifica la integridad de la Firebase API Key
y sincroniza el estado de tareas del sistema ABVETOS Intelligence.

Patente: PCT/EP2025/067317 — Protocolo Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os


class AbvetosTaskRunner:
    TASK_ID = "1b0d7405-aff9-465a-b680-92133b499ba8"
    SIREN = "943610196"

    def verify_firebase_integrity(self) -> str:
        """Comprueba que la API Key no sea nula y tenga el formato correcto."""
        api_key = os.environ.get("VITE_FIREBASE_API_KEY") or os.environ.get(
            "FIREBASE_API_KEY"
        )

        if not api_key:
            return "❌ ERROR: API Key ausente en el entorno local."

        if not api_key.startswith("AIza"):
            return "❌ ERROR: Formato de Firebase API Key inválido (Debe empezar por AIza)."

        return "✅ INTEGRIDAD DE KEY: Validada."

    def sync_task_status(self) -> None:
        """Verifica la integridad de la Firebase API Key e imprime el resultado."""
        print(f"📡 Sincronizando tarea {self.TASK_ID}...")
        status = self.verify_firebase_integrity()
        print(status)

        if "✅" in status:
            print("🚀 Tarea lista para SUPERCOMMIT. Destino: Payout 09:00 AM.")
        else:
            print("⚠️ Bloqueo detectado. Corrige el .env antes de continuar.")
