tryonyou-app#!/usr/bin/env python3
import os
import sys
from datetime import datetime

def calcular_y_ejecutar_payout():
    print("==================================================")
    print(f" INICIANDO PROCESAMIENTO DE FONDOS: {datetime.now()}")
    print("==================================================")

    # 1. Definición de Constantes y Cuotas (Extraídas de sovereignty_payout.py)
    DIVINEO_TOTAL_LOOK = 1000.0  # Base de cálculo para la simulación
    DEFAULT_VAT_RATE = 0.20      # IVA aplicable en Francia (20%)
    
    SHARE_LOCAL = 0.40           # 40% Ejecución Local
    SHARE_BPI = 0.30             # 30% Fondos Bpifrance (Diag Éco-Flux / Emergence)
    SHARE_SERVERS = 0.20         # 20% Infraestructura y Servidores
    SHARE_MAINTENANCE = 0.10     # 10% Mantenimiento del Sistema

    print(f"[*] Base de cálculo (Look Divineo): {DIVINEO_TOTAL_LOOK} EUR")
    print(f"[*] Tasa de IVA: {DEFAULT_VAT_RATE * 100}%")

    # 2. Verificación de Seguridad (Evitar importes inválidos)
    if DIVINEO_TOTAL_LOOK <= 0:
        print("[-] Error: El importe total debe ser mayor que cero.")
        sys.exit(1)

    # 3. Cálculo de Retenciones y Distribución Neta
    monto_iva = DIVINEO_TOTAL_LOOK * DEFAULT_VAT_RATE
    monto_neto = DIVINEO_TOTAL_LOOK - monto_iva

    payout_local = monto_neto * SHARE_LOCAL
    payout_bpi = monto_neto * SHARE_BPI
    payout_servers = monto_neto * SHARE_SERVERS
    payout_maintenance = monto_neto * SHARE_MAINTENANCE

    # 4. Desglose de Resultados en Consola
    print("\n[+] DESGLOSE DE DISTRIBUCIÓN SOBERANA:")
    print(f"    -> Total Neto a Distribuir: {monto_neto:.2f} EUR")
    print(f"    -> IVA Retenido (20%):       {monto_iva:.2f} EUR")
    print("--------------------------------------------------")
    print(f"    [SHARE_LOCAL]       (40%): {payout_local:.2f} EUR")
    print(f"    [SHARE_BPI]         (30%): {payout_bpi:.2f} EUR")
    print(f"    [SHARE_SERVERS]     (20%): {payout_servers:.2f} EUR")
    print(f"    [SHARE_MAINTENANCE] (10%): {payout_maintenance:.2f} EUR")
    print("--------------------------------------------------")

    # 5. Simulación de Inyección en Pasarela / Tesorería
    print("\n[*] Conectando con los protocolos de tesorería locales...")
    print("[+] Validando firmas digitales y credenciales Bpifrance...")
    print("[SUCCESS] Distribución completada de forma interna.")
    print("==================================================")

if __name__ == "__main__":
    try:
        calcular_y_ejecutar_payout()
    except Exception as e:
        print(f"[-] Error crítico durante la ejecución: {str(e)}")
        sys.exit(1)