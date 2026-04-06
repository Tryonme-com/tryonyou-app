Espejo Digital -> Make
import requests
import json
import os
from datetime import datetime

class DivineoAutomation:
    """
    Orquestador para automatizaciones entre el Espejo Digital y Make.
    Sincroniza métricas de usuario, selección de looks y alertas técnicas.
    """
    
    def __init__(self, make_webhook_url):
        self.webhook_url = make_webhook_url
        self.headers = {'Content-Type': 'application/json'}

    def sync_pilot_metrics(self, user_data, look_data, action_type):
        """
        Envía los datos del piloto a Make para procesar en Divineo_Leads_DB.
        Acciones: 'seleccion_perfecta', 'reserva_probador', 'silueta'.
        """
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_data.get("id"),
            "action": action_type,
            "look_details": {
                "brand": look_data.get("brand", "Lafayette"),
                "garment_id": look_data.get("id"),
                "size_confirmed": look_data.get("size")
            },
            "metadata": {
                "source": "digital_mirror_v1",
                "environment": "production"
            }
        }

        try:
            # Validación interna antes del envío
            if not self.webhook_url:
                raise ValueError("URL de Webhook de Make no configurada.")
            
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload), 
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"status": "success", "msg": f"Evento {action_type} sincronizado."}
            else:
                return {"status": "error", "code": response.status_code}
                
        except Exception as e:
            return {"status": "critical_error", "detail": str(e)}

# --- CONFIGURACIÓN DE EJECUCIÓN ---
# Reemplaza con la URL generada en tu escenario de Make
MAKE_WEBHOOK = "https://hook.eu1.make.com/tu_id_de_webhook"

# Ejemplo de uso para la función "Mi Selección Perfecta"
tracker = DivineoAutomation(MAKE_WEBHOOK)

test_user = {"id": "user_88_pau"}
test_look = {"brand": "Balmain", "id": "BLM-992", "size": "M"}

# Ejecución de prueba
resultado = tracker.sync_pilot_metrics(test_user, test_look, "seleccion_perfecta")
print(resultado)
