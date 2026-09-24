import os, csv; from datetime import datetime; import stripe; stripe.api_key = os.getenv("STRIPE_SECRET_KEY");
def run():
    if not stripe.api_key: print("❌ Sin clave"); return
    try:
        p = stripe.Payout.list(limit=100)
        with open("payouts_reales.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["ID Payout", "Cantidad", "Moneda", "Estado", "Fecha Llegada"])
            for i in p.auto_paging_iter(): w.writerow([i.id, f"{i.amount/100:.2f}", i.currency.upper(), i.status, datetime.fromtimestamp(i.arrival_date).strftime("%Y-%m-%d %H:%M:%S")])
        print("✅ Payouts listos.")
    except Exception as e: print(f"❌ Error Payouts: {e}")
    try:
        t = stripe.BalanceTransaction.list(limit=100, created={"gte": 1703980800})
        with open("transacciones_confirmadas.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["ID Transaccion", "Bruto", "Comision", "Neto", "Tipo", "Fecha UTC"])
            for i in t.auto_paging_iter(): w.writerow([i.id, f"{i.amount/100:.2f}", f"{i.fee/100:.2f}", f"{i.net/100:.2f}", i.type, datetime.fromtimestamp(i.created).strftime("%Y-%m-%d %H:%M:%S")])
        print("✅ Transacciones listas.")
    except Exception as e: print(f"❌ Error Transacciones: {e}")
if __name__ == "__main__": run()
