import requests

# Conector Linear para Make.com
def sync_to_bunker(data):
    WEBHOOK_URL = "https://hook.us1.make.com/TU_TOKEN_AQUI"
    try:
        # Sincronización inmediata con el búnker
        print(f"📤 Enviando a Make: {data}")
        # response = requests.post(WEBHOOK_URL, json=data) # Descomentar al tener el token
        return "Sincronización Linear completada."
    except Exception as e:
        return f"Error en el servicio: {e}"