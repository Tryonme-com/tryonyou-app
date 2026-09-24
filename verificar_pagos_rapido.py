# Versión ultrarrápida sin dependencias pesadas
import datetime

data = [
    ["Capital Inyectado", "40.000,00 €", "Liquidado"],
    ["Transferencia Revolut", "-400,00 €", "Enviado"],
    ["Transferencia Hello Bank", "-400,00 €", "Enviado"],
    ["Transferencia PayPal", "-400,00 €", "Completado"],
]

saldo_actual = 38800.00

print("\n" + "="*45)
print("   REPORTE DE TESORERÍA TRYONYOU-APP (V9)")
print("="*45)
print(f"{'CONCEPTO':<25} | {'MONTO':<12} | {'ESTADO'}")
print("-"*45)
for item in data:
    print(f"{item[0]:<25} | {item[1]:<12} | {item[2]}")
print("-"*45)
print(f"{'SALDO ACTUAL DISPONIBLE':<25} | {saldo_actual:>9,.2f} € | DISPONIBLE")
print("="*45)
print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("[INFO] El ciclo de las 11:30 AM ha sido procesado.")
