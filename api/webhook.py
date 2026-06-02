from __future__ import annotations

import uuid
from typing import Any

import stripe
from flask import Response, jsonify, request

from api.services.event_store import EventStore
from api.services.queue_service import QueueService
from api.services.redis_client import get_redis
from api.services.stripe_service import construct_event
from api.utils.logging import get_logger

logger = get_logger("stripe_webhook")


def process_stripe_webhook() -> tuple[Response, int]:
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    payload = request.get_data(cache=False, as_text=False)
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = construct_event(payload, sig_header)
    except ValueError:
        return jsonify({"status": "invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"status": "invalid signature"}), 400
    except RuntimeError:
        logger.error("webhook_misconfigured", extra={"trace_id": trace_id, "status": "error"})
        return jsonify({"status": "misconfigured"}), 500

    event_id = event.get("id", "")
    event_type = event.get("type", "unknown")
    if not event_id:
        return jsonify({"status": "invalid event"}), 400

    redis = get_redis()
    store = EventStore(redis)
    queue = QueueService(redis)

    if not store.mark_received_once(event_id):
        logger.info("duplicate_event", extra={"event_id": event_id, "event_type": event_type, "trace_id": trace_id, "status": "ignored"})
        return jsonify({"status": "duplicate"}), 200

    store.persist_received_event(event, trace_id)
    queue.enqueue(event_id, trace_id, attempts=0)
    store.update_status(event_id, "queued", attempts=0)

    logger.info("event_enqueued", extra={"event_id": event_id, "event_type": event_type, "trace_id": trace_id, "status": "queued"})
    return jsonify({"status": "accepted"}), 200
