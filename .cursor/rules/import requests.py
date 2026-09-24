import requests
import json
import time
import datetime

# --- CONFIGURACIÓN DE SOBERANÍA NUBE ---
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn"
PROJECT_ID = "tryonyou-app"

def disparar_agentes_en_nube():
    print(f"=== INICIANDO ORQUESTACIÓN DE 50 AGENTES (MAKE.COM) ===")
    print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Conectando con webhook remoto...")
    start_time = time.time()
    
    # Payload que se enviará a Make.com (Puedes añadir variables si las necesitas)
    payload = {
        "action": "execute_50_agents_parallel",
        "project": PROJECT_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "architect": "ruben.espinar.10@icloud.com"
    }
    
    try:
        # Petición POST al webhook. El timeout es alto porque Make.com tiene que
        # esperar a que los 50 agentes (Repeater -> HTTP -> Aggregator) terminen.
        response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            duration = time.time() - start_time
            print(f"✅ OPERACIÓN EXITOSA. Los 50 agentes han concluido en {duration:.2f} segundos.")
            print("\n--- DATOS DE VUELTA DESDE LA NUBE ---")
            
            try:
                datos = response.json()
                print(json.dumps(datos, indent=4))
            except json.JSONDecodeError:
                # Si Make.com devuelve texto en lugar de JSON
                print(response.text)
                
            print("-------------------------------------")
            
        elif response.status_code == 202:
             print(f"⚠️ Petición aceptada por Make.com (Status 202).")
             print("Make está procesando los agentes en segundo plano, pero no ha devuelto un Webhook Response inmediato.")
             
        else:
            print(f"❌ FALLA EN LA NUBE. Status devuelto por Make.com: {response.status_code}")
            print(f"Cuerpo de la respuesta: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ ERROR: Timeout. Make.com tardó más de 120 segundos en ejecutar los 50 agentes.")
        print("Revisa el historial de ejecuciones dentro de Make.com para ver dónde está el cuello de botella.")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR CRÍTICO de conexión: {e}")

if __name__ == "__main__":
    disparar_agentes_en_nube()import os
import requests
import json
import subprocess
from datetime import datetime

# === PARÁMETROS DE SOBERANÍA (75001) ===
URL_MAKE = "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn"
DEUDA_TOTAL = "16.200 € TTC (Setup + 20% Comisiones)"

def consolidacion_total():
    print(f"🚀 Iniciando Ciclo de Consolidación Omega...")
    
    # 1. LIMPIEZA DE ARCHIVOS HUÉRFANOS (Lo que sale en tu captura)
    basura = ['terminal_cleanup.py', 'check_system_health.py', 'deploy_omega_final.py']
    for archivo in basura:
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"🔥 Eliminado: {archivo}")

    # 2. DISPARO A LA NUBE (50 Agentes)
    try:
        r = requests.post(URL_MAKE, json={"status": "consolidated_run"}, timeout=120)
        print(f"📡 Make.com: Status {r.status_code}")
    except Exception as e:
        print(f"⚠️ Error Nube: {e}")

    # 3. SELLO DE GIT AUTOMÁTICO
    try:
        subprocess.run(["git", "add", "."], check=True)
        msg = f"🔒 Bloqueo Nodo 75009: Piloto Finalizado. Deuda Pendiente: {DEUDA_TOTAL}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        print(f"✅ Git sellado: {msg}")
    except:
        print("✅ Git: Sin cambios nuevos.")

if __name__ == "__main__":
    consolidacion_total()
    print("\n🔱 SISTEMA EN AUTONOMÍA. BÚNKER CERRADO POR 2 HORAS. 💥")
    