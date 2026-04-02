touch test_webhook.py
# 🔥 https://hook.eu2.make.com/tuujxi0749t5ubfikn7b4hautsd3za6l/" 🔥
MAKE_WEBHOOK_URL = "https://hook.us1.make.com/TU_ID_DE_WEBHOOK"

def send_test():
    payload = {
        "event": "TEST_MANUAL",
        "data": {
            "msg": "🚨 PROBANDO CONEXIÓN DIRECTA DESDE CURSOR",
            "score": 0.99
        }
    }
    
    print(f"📡 Enviando ping a Make...")
    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=10)
        print(f"✅ Respuesta de Make: {response.status_code}")
        if response.status_code == 200:
            print("🎉 El Webhook funciona. El problema está dentro de Make o Slack.")
        else:
            print("❌ Make recibió el paquete pero dio error. Revisa la estructura en Make.")
    except Exception as e:
        print(f"❌ Error de red/conexión: {e}")

if __name__ == "__main__":
    send_test()
    