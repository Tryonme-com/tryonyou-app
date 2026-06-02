"""
Centralised configuration — all values read from environment variables.

Usage:
    from config import Config
    secret = Config.STRIPE_ENDPOINT_SECRET

Call Config.validate() once at startup (not per-request) to fail fast on
missing required variables.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class Config:
    # ── App ───────────────────────────────────────────────────────────────────
    APP_ENV: str = os.environ.get("APP_ENV", "development")
    PORT: int = int(os.environ.get("PORT", "4242"))
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # ── Stripe ────────────────────────────────────────────────────────────────
    STRIPE_API_KEY: str = os.environ.get("STRIPE_API_KEY", "").strip()
    STRIPE_ENDPOINT_SECRET: str = os.environ.get("STRIPE_ENDPOINT_SECRET", "").strip()

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = os.environ.get("REDIS_URL", "").strip()
    REDIS_QUEUE_KEY: str = os.environ.get("REDIS_QUEUE_KEY", "stripe:queue:pending")
    REDIS_DLQ_KEY: str = os.environ.get("REDIS_DLQ_KEY", "stripe:queue:dlq")
    REDIS_LOCK_TTL: int = int(os.environ.get("REDIS_LOCK_TTL", "30"))
    # How long to keep event metadata in Redis (default 7 days)
    REDIS_EVENT_TTL: int = int(os.environ.get("REDIS_EVENT_TTL", str(86_400 * 7)))

    # ── AI providers ──────────────────────────────────────────────────────────
    AI_PROVIDER: str = os.environ.get("AI_PROVIDER", "").strip().lower()
    GOOGLE_AI_API_KEY: str = os.environ.get("GOOGLE_AI_API_KEY", "").strip()
    GOOGLE_AI_MODEL: str = os.environ.get("GOOGLE_AI_MODEL", "gemini-1.5-flash")
    MANUS_API_KEY: str = os.environ.get("MANUS_API_KEY", "").strip()
    MANUS_BASE_URL: str = (
        os.environ.get("MANUS_BASE_URL", "https://api.manus.ai/v1").rstrip("/")
    )
    MANUS_TIMEOUT_S: float = float(os.environ.get("MANUS_TIMEOUT_S", "10"))

    # ── Jules worker ──────────────────────────────────────────────────────────
    MAX_RETRIES: int = int(os.environ.get("MAX_RETRIES", "3"))
    WORKER_POLL_TIMEOUT: int = int(os.environ.get("WORKER_POLL_TIMEOUT", "5"))

    @classmethod
    def validate(cls) -> None:
        """
        Raise RuntimeError on missing critical config.
        Call once at startup — never per-request.
        """
        missing = [
            name
            for name, value in [
                ("STRIPE_ENDPOINT_SECRET", cls.STRIPE_ENDPOINT_SECRET),
            ]
            if not value
        ]
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        if cls.STRIPE_API_KEY:
            import stripe
            stripe.api_key = cls.STRIPE_API_KEY

    @classmethod
    def is_production(cls) -> bool:
        return cls.APP_ENV == "production"
