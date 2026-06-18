import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def procesar_cobro(monto, email, desc):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(monto * 100),
            currency='eur',
            receipt_email=email,
            description=desc,
            automatic_payment_methods={"enabled": True},
        )
        print(f"ÉXITO: Cobro creado. ID: {intent.id}")
        print(f"Client Secret: {intent.client_secret}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    procesar_cobro(100.0, "cliente@ejemplo.com", "Pago de deuda")
