import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv('STRIPE_API_KEY')

def cobrar_a_cliente(monto_euros, email_cliente, descripcion="Cobro tryonyou"):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(monto_euros * 100),
            currency='eur',
            receipt_email=email_cliente,
            description=descripcion,
            automatic_payment_methods={"enabled": True},
        )
        return intent
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Prueba rápida de creación de cobro
    resultado = cobrar_a_cliente(10.00, "cliente@ejemplo.com", "Prueba de pago real")
    print(resultado)
