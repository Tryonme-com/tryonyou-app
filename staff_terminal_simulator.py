import asyncio
import json
import time

async def staff_terminal_simulator():
    """
    Simula el terminal del personal de Galeries Lafayette.
    Escucha una reserva de probador y confirma la asignación.
    """
    print("🧥 [STAFF TERMINAL] Iniciando escucha de WebSocket...")
    print("📡 [STAFF TERMINAL] Conectado al servidor de Galeries Lafayette (Haussmann)")
    
    # Simular espera de mensaje
    await asyncio.sleep(2)
    
    # Simular recepción de mensaje de reserva
    reservation_msg = {
        "type": "FITTING_ROOM_RESERVATION",
        "user_id": "VIP_001",
        "garment_id": "BLM-JKT-09",
        "garment_name": "Balmain Structured Blazer",
        "size": "38 (M)",
        "timestamp": time.time()
    }
    
    print(f"\n🔔 [STAFF TERMINAL] ¡Nueva reserva recibida!")
    print(f"   - Prenda: {reservation_msg['garment_name']} ({reservation_msg['garment_id']})")
    print(f"   - Talla: {reservation_msg['size']}")
    print(f"   - Cliente: {reservation_msg['user_id']}")
    
    # Simular procesamiento y asignación de probador
    await asyncio.sleep(1.5)
    
    confirmation_msg = {
        "type": "RESERVATION_CONFIRMED",
        "room_id": "VIP-01",
        "status": "READY",
        "staff_id": "NICOLAS_T",
        "timestamp": time.time()
    }
    
    print(f"\n✅ [STAFF TERMINAL] Probador asignado: {confirmation_msg['room_id']}")
    print(f"   - Estado: {confirmation_msg['status']}")
    print(f"   - Encargado: {confirmation_msg['staff_id']}")
    
    # Guardar log de la transacción
    log = {
        "received": reservation_msg,
        "sent": confirmation_msg
    }
    with open("staff_terminal_log.json", "w") as f:
        json.dump(log, f, indent=2)
        
    print("\n📊 [STAFF TERMINAL] Log de transacción guardado.")

if __name__ == "__main__":
    asyncio.run(staff_terminal_simulator())
