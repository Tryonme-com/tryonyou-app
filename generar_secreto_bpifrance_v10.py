"""
Referencia interna determinista (SHA-256 truncado) a partir de SIRET + patente + estado.

⚠️ No es un token emitido por Bpifrance. No sustituye credenciales ni flujos del portal
   real; usar solo como etiqueta interna / narrativa si encaja con vuestro protocolo.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import hashlib

SIRET = "94361019600017"
PATENTE = "PCT/EP2025/067317"
STATUS = "DEEPTECH_VALIDATED"
FOUNDER_REF = "Rubén Espinar Rodríguez"


def generar_secreto_bpifrance() -> str:
    """
    Devuelve una cadena tipo BPI-XXXXXXXXXXXX-V10 derivada de activos registrados (demo).
    """
    seed = f"{SIRET}-{PATENTE}-{STATUS}-2026"
    secret_hash = hashlib.sha256(seed.encode()).hexdigest()[:12].upper()
    token = f"BPI-{secret_hash}-V10"

    print("\n" + "═" * 55)
    print("🏛️  SISTEMA DE REFERENCIA INTERNA — PUENTE BPI (DEMO)")
    print("═" * 55)
    print("📦 ENTIDAD: TRYONYOU SAS")
    print(f"🛡️  SIRET:   {SIRET}")
    print(f"📜 PATENTE: {PATENTE}")
    print(f"👤 REF. FUNDADOR: {FOUNDER_REF}")
    print("─" * 55)
    print(f"🔑 BPIFRANCE_SECRET_VALUE: {token}")
    print("─" * 55)
    print("Solo referencia interna; verificar siempre en mon.bpifrance.fr y con tu gestor.")
    print("═" * 55 + "\n")
    return token


if __name__ == "__main__":
    generar_secreto_bpifrance()
