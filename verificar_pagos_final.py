import pandas as pd

# Estado de la cuenta tras las tres transferencias de 400€
data = {
    'Concepto': ['Capital Inyectado Hoy', 'Transferencia Revolut', 'Transferencia Hello Bank', 'Transferencia PayPal', 'SALDO ACTUAL'],
    'Monto_EUR': [40000.0, -400.0, -400.0, -400.0, 38800.0],
    'Estado': ['Liquidado', 'Enviado', 'Enviado', 'Completado', 'DISPONIBLE']
}

df = pd.DataFrame(data)

print("\n--- REPORTE DE TESORERÍA TRYONYOU-APP ---")
print(df.to_string(index=False))
print("\n[INFO] El ciclo de las 11:30 AM ha procesado las salidas.")
print("[!] Saldo remanente en cuenta V7: 38.800,00 €")
