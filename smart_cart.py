import json

def add_to_perfect_cart(item_name, detected_size):
    # El valor del piloto: reducción de devoluciones por talla correcta
    cart_entry = {
        "item": item_name,
        "size_confirmed": detected_size,
        "algorithm_version": "v10_ultimate",
        "client_id": "gen-lang-client-0091228222",
        "action": "ADD_TO_CART"
    }
    
    print(f"\n[🛒 CART] Añadiendo {item_name}...")
    print(f"[📏 TALLA] Ajuste confirmado: {detected_size}")
    
    # Guardamos la intención de compra para métricas
    with open('cart_logs.json', 'a') as f:
        f.write(json.dumps(cart_entry) + "\n")
        
    return "✅ Producto añadido con éxito. Sin errores de talla."

if __name__ == "__main__":
    # Simulación: El espejo detecta que eres una "L" en Balmain
    print(add_to_perfect_cart("Balmain Signature Jacket", "L"))
