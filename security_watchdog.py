import os
import time
import subprocess

def monitor_vault():
    vault_file = "master_omega_vault.json"
    print(f"--- 🛡️ ACTIVANDO MODO CENTINELA: PROTEGIENDO {vault_file} ---")
    
    # Obtener el hash inicial del archivo
    def get_git_status():
        return subprocess.getoutput(f"git status --porcelain {vault_file}")

    try:
        while True:
            status = get_git_status()
            if status:
                print("⚠️ ALERTA DE SEGURIDAD: Intento de modificación detectado.")
                print("Restaurando integridad del sistema desde el Búnker GitHub...")
                os.system(f"git checkout {vault_file}")
                print("✅ Integridad restaurada. Sello del Fundador intacto.")
            
            time.sleep(10) # Vigilancia cada 10 segundos
    except KeyboardInterrupt:
        print("\n--- 🛑 MODO CENTINELA DESACTIVADO POR EL FUNDADOR ---")

if __name__ == "__main__":
    monitor_vault()
