from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    port: int = int(os.getenv("PORT", "4242"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    stripe_api_key: str = os.getenv("STRIPE_API_KEY", "")
    # STRIPE_SECRET_KEY is the canonical name; fall back to STRIPE_API_KEY for
    # backward compatibility with existing deployments.
    stripe_secret_key: str = os.getenv(
        "STRIPE_SECRET_KEY", os.getenv("STRIPE_API_KEY", "")
    )
    stripe_endpoint_secret: str = os.getenv("STRIPE_ENDPOINT_SECRET", "")

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_queue_key: str = os.getenv("REDIS_QUEUE_KEY", "stripe:events:queue")
    redis_dead_letter_key: str = os.getenv("REDIS_DEAD_LETTER_KEY", "stripe:events:dlq")
    redis_retry_key: str = os.getenv("REDIS_RETRY_KEY", "stripe:events:retry")

    event_ttl_seconds: int = int(os.getenv("EVENT_TTL_SECONDS", "604800"))
    lock_ttl_seconds: int = int(os.getenv("LOCK_TTL_SECONDS", "60"))
    max_retry_attempts: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "5"))
    retry_backoff_base_seconds: int = int(os.getenv("RETRY_BACKOFF_BASE_SECONDS", "2"))
    retry_max_backoff_seconds: int = int(os.getenv("RETRY_MAX_BACKOFF_SECONDS", "300"))
    max_error_length: int = int(os.getenv("MAX_ERROR_LENGTH", "600"))
    worker_pop_timeout_seconds: int = int(os.getenv("WORKER_POP_TIMEOUT_SECONDS", "2"))

    ai_provider: str = os.getenv("AI_PROVIDER", "google")
    ai_timeout_seconds: int = int(os.getenv("AI_TIMEOUT_SECONDS", "20"))
    google_ai_api_key: str = os.getenv("GOOGLE_AI_API_KEY", "")
    manus_api_key: str = os.getenv("MANUS_API_KEY", "")
    manus_base_url: str = os.getenv("MANUS_BASE_URL", "")


settings = Settings()
