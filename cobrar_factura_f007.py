import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def generar_cobro_factura():
    try:
        intent = stripe.PaymentIntent.create(
            amount=3988800,
            currency='eur',
            receipt_email='elena.grandini@galerieslafayette.com',
            description='Factura F-2026-007 - TRYONYOU',
            metadata={'invoice_id': 'F-2026-007', 'siren': '943610196'},
            automatic_payment_methods={"enabled": True},
        )
        print(f"COBRO CREADO CON ÉXITO.")
        print(f"ID del pago: {intent.id}")
        print(f"Client Secret (Enviar al cliente): {intent.client_secret}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    generar_cobro_factura()
