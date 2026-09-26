from __future__ import annotations

from flask import Flask

from api.webhook import process_stripe_webhook


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/api/webhook", methods=["POST"])
    def webhook():
        return process_stripe_webhook()

    return app
