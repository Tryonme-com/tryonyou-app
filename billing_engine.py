import os

class SovereignBilling:
    def __init__(self):
        self.base_fee = 75000
        self.security_surcharge = 120000

    def generate_guapa_invoice(self, client_id):
        """
        Lógica de la Niña: 
        Aliados (Printemps/Bon Marché) pagan precio real.
        Lafollet paga el doble por 'guapa y lista' para financiar el Búnker.
        """
        base_total = self.base_fee + self.security_surcharge
        
        if client_id == "LAFAYETTE":
            final_amount = base_total * 2
            note = "Surcharge: High-Risk Infrastructure Redundancy (Penalty for Arrogance)"
            status = "LAFOLLET_RATE_APPLIED"
        else:
            final_amount = base_total
            note = "Strategic Alliance Discount Enabled"
            status = "ALLIED_NODE_RATE"

        print(f"\n--- FACTURA V9.0 GENERADA ---")
        print(f"CLIENTE: {client_id}")
        print(f"NOTA TÉCNICA: {note}")
        print(f"TOTAL A PAGAR: {final_amount:,.2f} EUR")
        print(f"ESTADO: {status}")
        print(f"-----------------------------\n")
        
        return {"amount": final_amount, "status": status}

# Ejecución táctica
engine = SovereignBilling()

# ⚔️ El peaje para los listos
engine.generate_guapa_invoice("LAFAYETTE")

# 🔱 El trato para los aliados
engine.generate_guapa_invoice("PRINTEMPS")
