import json
import time
import os

def run_demo():
    print("="*40)
    print("🚀 TRYONYOU-APP | ESPEJO DIGITAL v1.1")
    print("="*40)
    print("ID Sesión: gen-lang-client-0091228222")
    print("Organización: Tryonme-com")
    print("-"*40)

    # 1. Simulación de Escaneo (Botón 4)
    print("\n[PASO 1] Iniciando Escaneo de Silueta...")
    time.sleep(1)
    measurements = {"height": 180, "chest": 100, "waist": 85}
    from save_silhouette import save_secure_silhouette
    print(save_secure_silhouette(measurements))

    # 2. Selección de Prenda y Carrito (Botón 1)
    print("\n[PASO 2] El usuario selecciona: Balmain Signature Jacket")
    time.sleep(1)
    from smart_cart import add_to_perfect_cart
    print(add_to_perfect_cart("Balmain Signature Jacket", "L"))

    # 3. Reserva en Tienda (Botón 2)
    print("\n[PASO 3] Generando Reserva para Probador...")
    time.sleep(1)
    from qr_generator import generate_store_qr
    print(generate_store_qr("BAL-JKT-001", "L"))

    print("\n" + "="*40)
    print("✅ DEMO FINALIZADA CON ÉXITO")
    print("Métricas guardadas en: cart_logs.json y user_silhouette.json")
    print("="*40)

if __name__ == "__main__":
    run_demo()
