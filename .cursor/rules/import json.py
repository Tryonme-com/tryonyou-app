import json
from datetime import datetime

# CONFIGURACIÓN DE IDENTIDAD DIVINEO V9
IDENTITY = {
    "company": "DIVINEO V9",
    "siren": "943 610 196",
    "patent": "PCT/EP2025/067317",
    "precision": "0.08mm",
    "location": "Paris, France"
}

AUTO_REPLY_TEMPLATE = f"""
[DIVINEO V9 - AUTOMATED TECHNICAL RESPONSE]

Bonjour, 

Merci de nous avoir contactés via le canal VIP. 
Votre demande est en cours d'analyse par notre système de souveraineté biométrique.

DÉTAILS TECHNIQUES DE L'ENTITÉ :
- Enregistrement : SIREN {IDENTITY['siren']}
- Technologie : Brevet {IDENTITY['patent']}
- Standard de Précision : {IDENTITY['precision']}

POUR ACCÉLÉRER VOTRE DOSSIER, VEUILLEZ PRÉCISER :
1. Type de projet (Luxe / Prêt-à-porter / Tech API)
2. Volume d'actifs (Nombre de patrons ou SKUs)
3. Date cible pour l'implémentation (Hito Mayo 2026 disponible)

Un ingénieur de notre bureau de Paris reviendra vers vous.
---------------------------------------------------------
Precision is not a luxury; it's our Sovereignty.
"""

def analyze_client_message(message):
    """
    Script para que Cursor clasifique al cliente.
    """
    high_value_keywords = ["luxe", "luxury", "api", "precision", "biometric", "paris", "0.08"]
    is_high_value = any(word in message.lower() for word in high_value_keywords)
    
    status = "⭐️ ALTO VALOR (Lujo/Tech)" if is_high_value else "⚠️ BAJO VALOR / RUIDO"
    
    print(f"\n--- ANÁLISIS DE CLIENTE ({datetime.now().strftime('%H:%M')}) ---")
    print(f"Estado: {status}")
    print(f"Respuesta sugerida: ENVIAR AUTO-REPLY V9")
    return is_high_value

# Guardar la respuesta para tenerla a mano en Cursor
with open("FIVERR_AUTO_REPLY.txt", "w") as f:
    f.write(AUTO_REPLY_TEMPLATE)

print("✅ Agente configurado. Auto-reply guardado en FIVERR_AUTO_REPLY.txt")
