import json
import random

def get_inventory_status(brand, look_id, size):
    """
    Simula una llamada a la API de inventario en tiempo real.
    """
    # Simulación: Balmain tiene poco stock en talla M
    if brand == "BALMAIN" and size == "38 (M)":
        return False # Agotado
    return True # Disponible

def inventory_sync_logic(biometric_output):
    """
    Conecta la salida biométrica con la API de inventario.
    Si la talla recomendada para Balmain no está disponible, sugiere Burberry.
    """
    print(f"📦 [INVENTORY SYNC] Procesando recomendación biométrica: {biometric_output['recommendation']}")
    
    selected_look = {
        "id": "LAF-BAL-001",
        "brand": "BALMAIN",
        "name": "Blazer Structuré Noir Absolu",
        "size": biometric_output['recommendation']
    }
    
    is_available = get_inventory_status(selected_look['brand'], selected_look['id'], selected_look['size'])
    
    if not is_available:
        print(f"⚠️ [INVENTORY SYNC] Talla {selected_look['size']} para {selected_look['brand']} no disponible.")
        print(f"🔄 [INVENTORY SYNC] Buscando alternativa de lujo (Burberry)...")
        
        # Fallback a Burberry
        fallback_look = {
            "id": "LAF-BUR-002",
            "brand": "BURBERRY",
            "name": "Trench Coat Heritage Kensington",
            "size": selected_look['size'],
            "reason": "Alternative d'exception (Burberry elegance)"
        }
        
        print(f"✅ [INVENTORY SYNC] Sugerencia automática: {fallback_look['brand']} {fallback_look['name']}")
        return {
            "status": "FALLBACK_APPLIED",
            "original": selected_look,
            "suggested": fallback_look
        }
    else:
        print(f"✅ [INVENTORY SYNC] Look {selected_look['brand']} disponible en talla {selected_look['size']}.")
        return {
            "status": "AVAILABLE",
            "selected": selected_look
        }

def run_inventory_test():
    # Caso 1: Talla M (Agotada en Balmain -> Fallback a Burberry)
    print("\n--- Test Caso 1: Talla M (Agotada) ---")
    biometric_m = {"recommendation": "38 (M)"}
    result_m = inventory_sync_logic(biometric_m)
    
    # Caso 2: Talla S (Disponible en Balmain)
    print("\n--- Test Caso 2: Talla S (Disponible) ---")
    biometric_s = {"recommendation": "36 (S)"}
    result_s = inventory_sync_logic(biometric_s)
    
    # Guardar resultados
    results = {
        "case_m": result_m,
        "case_s": result_s
    }
    with open("inventory_sync_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Resultados de sincronización guardados en: inventory_sync_results.json")

if __name__ == "__main__":
    run_inventory_test()
