from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_API_KEY')

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        amount = data.get('amount', 1000)
        intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency='eur',
            automatic_payment_methods={"enabled": True},
        )
        return jsonify({'client_secret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=4242)
