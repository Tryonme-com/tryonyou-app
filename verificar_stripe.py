import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv('STRIPE_API_KEY')

try:
    account = stripe.Account.retrieve()
    balance = stripe.Balance.retrieve()
    name = getattr(account, 'display_name', 'Nombre no configurado')
    print("--- CONEXIÓN EXITOSA ---")
    print(f"Cuenta: {name}")
    if balance.available:
        print(f"Saldo disponible: {balance.available[0].amount / 100} {balance.available[0].currency.upper()}")
    else:
        print("Saldo disponible: 0.00")
except Exception as e:
    print(f"ERROR DETALLADO: {e}")
