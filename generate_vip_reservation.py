import json
import uuid
from datetime import datetime

def create_ticket(client_name="VIP Client", look_id="BALMAIN_GOLD_V10"):
    print(f"--- 🎟️ GENERANDO RESERVA VIP - TRYONYOU ---")
    
    reservation_id = f"TY-VIP-{str(uuid.uuid4())[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ticket = {
        "reservation_id": reservation_id,
        "founder": "Rubén Espinar Rodríguez",
        "patent_ref": "PCT/EP2025/067317",
        "siret": "94361019600017",
        "client": client_name,
        "look": look_id,
        "location": "Galeries Lafayette - Paris",
        "valid_until": "Mayo 2026",
        "status": "CONFIRMED"
    }
    
    filename = f"reservas/ticket_{reservation_id}.json"
    os.makedirs("reservas", exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(ticket, f, indent=4)
    
    print(f"✅ Ticket {reservation_id} generado.")
    print(f"🔗 Link de validación: https://tryonyou.app/verify?id={reservation_id}")
    return ticket

if __name__ == "__main__":
    import os
    create_ticket()
