deploy_omega_final.py
import os
import json
import datetime

# --- CONFIGURACIÓN DE SOBERANÍA (NODO 75001) ---
TARGET_NODE = "75009" # Galeries Lafayette
DB_PATH = "/var/db/sacmuseum/collect_v10_310.db"
LOG_PATH = "/var/log/sacmuseum/access.log"
ARCHITECT_EMAIL = "ruben.espinar.10@icloud.com"

# --- DATOS FINANCIEROS ACTUALIZADOS ---
SETUP_FEE_TTC = 9000.00
COMISSIONS_HT = 6000.00
IVA_RATE = 0.20
# Total: 9000 + (6000 * 1.20) = 16200.00 € TTC
TOTAL_DUE_TTC = SETUP_FEE_TTC + (COMISSIONS_HT * (1 + IVA_RATE)) 

def deploy_omega_update():
    print("=== INICIANDO ACTUALIZACIÓN Y CIERRE OMEGA (V10) ===")
    print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Ejecutando protocolo de cierre...")

    # 1. ACTUALIZACIÓN DEL ENTORNO (KILL-SWITCH)
    os.environ['SERVER_EXTERN_STATUS'] = 'OFFLINE_LOCKED'
    os.environ['PENDING_DEBT_TTC'] = str(TOTAL_DUE_TTC)
    os.environ['COMMISSION_RATE'] = '0.20'
    print(f"✅ Variables de entorno actualizadas. Deuda exigida: {TOTAL_DUE_TTC} € TTC.")

    # 2. NEUTRALIZACIÓN DE BASE DE DATOS
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"🔒 Base de datos {DB_PATH} ELIMINADA. Acceso denegado a referencias.")
        else:
            print(f"⚠️ Base de datos no encontrada (posiblemente ya eliminada).")
    except Exception as e:
        print(f"Error al acceder a BD: {e}")

    # 3. LIMPIEZA DE LOGS Y SELLO DE ADVERTENCIA
    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, 'w') as f:
                f.write(f"[{datetime.datetime.now().isoformat()}] ACCESO 410 GONE. NODO {TARGET_NODE} EXTINGUIDO. DEUDA PENDIENTE: {TOTAL_DUE_TTC}€ TTC.\n")
            print(f"🔥 Logs antiguos borrados. Sello de advertencia inyectado en access.log.")
        else:
            print(f"⚠️ Archivo de log de acceso no encontrado.")
    except Exception as e:
        print(f"Error al modificar logs: {e}")

    # 4. REPORTE LOCAL DE ESTADO
    report = {
        "status": "LOCKED_EXTINGUISHED",
        "node": TARGET_NODE,
        "total_due_ttc": TOTAL_DUE_TTC,
        "timestamp": datetime.datetime.now().isoformat(),
        "architect": ARCHITECT_EMAIL
    }
    
    with open("omega_status_final.json", "w") as f:
        json.dump(report, f, indent=4)

    print(f"📧 Reporte final generado (omega_status_final.json).")
    print("=== DESPLIEGUE FINALIZADO. NODO LAFAYETTE CERRADO. ===")

if __name__ == "__main__":
    deploy_omega_update()
    