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
    
    payload = {
        "action": "execute_50_agents_parallel",
        "project": PROJECT_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "architect": "ruben.espinar.10@icloud.com"
    }
    
    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            duration = time.time() - start_time
            print(f"✅ OPERACIÓN EXITOSA. Los 50 agentes han concluido en {duration:.2f} segundos.")
            print("\n--- DATOS DE VUELTA DESDE LA NUBE ---")
            
            try:
                datos = response.json()
                print(json.dumps(datos, indent=4))
            except json.JSONDecodeError:
                print(response.text)
                
            print("-------------------------------------")
            
        elif response.status_code == 202:
             print(f"⚠️ Petición aceptada por Make.com (Status 202).")
             print("Make está procesando en segundo plano.")
             
        else:
            print(f"❌ FALLA EN LA NUBE. Status devuelto por Make.com: {response.status_code}")
            print(f"Cuerpo de la respuesta: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ ERROR: Timeout. Make.com tardó más de 120 segundos.")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR CRÍTICO de conexión: {e}")

if __name__ == "__main__":
    disparar_agentes_en_nube()