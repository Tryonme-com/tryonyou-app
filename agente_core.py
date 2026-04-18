"""
Agente 70 — ciclo autónomo Golden Peacock (vigilancia liquidez / 402, validación leads).
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from typing import Any


class Agente70:
    """Hilo de vigilancia periódica alineado con FinancialGuard (awareness 402 en espejo)."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def validar_divineo_leads_db(self) -> bool:
        """Comprueba ruta SQLite si está definida en entorno (DIVINEO_LEADS_DB_PATH / LEADS_DB_PATH)."""
        path = (os.getenv("DIVINEO_LEADS_DB_PATH") or os.getenv("LEADS_DB_PATH") or "").strip()
        if not path:
            print("Divineo_Leads_DB: sin ruta en env (DIVINEO_LEADS_DB_PATH / LEADS_DB_PATH) — omitido.")
            return True
        if not os.path.isfile(path):
            print(f"Divineo_Leads_DB: archivo no encontrado: {path}")
            return False
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            try:
                conn.execute("SELECT 1").fetchone()
            finally:
                conn.close()
        except sqlite3.Error as e:
            print(f"Divineo_Leads_DB: error SQLite: {e}")
            return False
        print(f"Divineo_Leads_DB: conexión OK ({path}).")
        return True

    def _vigilancia_loop(self) -> None:
        while not self._stop.wait(timeout=60.0):
            try:
                from api.financial_guard import liquidity_ok

                if not liquidity_ok():
                    print(
                        "Agente70: vigilancia — liquidez bajo umbral "
                        "(FinancialGuard puede responder 402 en espejo / rutas no allowlist)."
                    )
            except Exception as e:
                print(f"Agente70: vigilancia (lectura liquidez): {e}")

    def start_autonomous_cycle(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._vigilancia_loop,
            name="Agente70-Vigilancia402",
            daemon=False,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
