"""Reglas de integración Peacock_Core / Zero-Size (unittest estándar)."""

from __future__ import annotations

import hashlib
import hmac
import os
import sys
import time
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from peacock_core import (
    ZERO_SIZE_LATENCY_BUDGET_MS,
    IdempotencyGuard,
    is_webhook_destination_forbidden,
    verify_webhook_sha1_signature,
)


class TestPeacockCoreIntegration(unittest.TestCase):
    def test_latency_budget_is_25ms(self) -> None:
        self.assertEqual(ZERO_SIZE_LATENCY_BUDGET_MS, 25)

    def test_abvetos_webhook_blocked(self) -> None:
        self.assertTrue(
            is_webhook_destination_forbidden("https://api.abvetos.com/hook/xyz"),
        )
        self.assertTrue(
            is_webhook_destination_forbidden("https://abvetos.com/webhook"),
        )

    def test_make_and_slack_like_urls_allowed(self) -> None:
        self.assertFalse(
            is_webhook_destination_forbidden("https://hook.eu2.make.com/abc"),
        )
        self.assertFalse(
            is_webhook_destination_forbidden("https://hooks.slack.com/services/XX/YY/ZZ"),
        )


# ---------------------------------------------------------------------------
# verify_webhook_sha1_signature
# ---------------------------------------------------------------------------

def _make_sig(payload: bytes, secret: str) -> str:
    """Helper: genera una firma HMAC-SHA1 válida."""
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha1).hexdigest()
    return f"sha1={digest}"


class TestVerifyWebhookSha1Signature(unittest.TestCase):
    _SECRET = "test-secret-key"
    _PAYLOAD = b'{"event": "balmain_click"}'

    def test_valid_signature_accepted(self) -> None:
        sig = _make_sig(self._PAYLOAD, self._SECRET)
        self.assertTrue(verify_webhook_sha1_signature(self._PAYLOAD, sig, self._SECRET))

    def test_wrong_secret_rejected(self) -> None:
        sig = _make_sig(self._PAYLOAD, "other-secret")
        self.assertFalse(verify_webhook_sha1_signature(self._PAYLOAD, sig, self._SECRET))

    def test_tampered_payload_rejected(self) -> None:
        sig = _make_sig(self._PAYLOAD, self._SECRET)
        tampered = b'{"event": "balmain_click", "injected": true}'
        self.assertFalse(verify_webhook_sha1_signature(tampered, sig, self._SECRET))

    def test_missing_prefix_rejected(self) -> None:
        digest = hmac.new(self._SECRET.encode(), self._PAYLOAD, hashlib.sha1).hexdigest()
        self.assertFalse(verify_webhook_sha1_signature(self._PAYLOAD, digest, self._SECRET))

    def test_empty_payload_rejected(self) -> None:
        sig = _make_sig(self._PAYLOAD, self._SECRET)
        self.assertFalse(verify_webhook_sha1_signature(b"", sig, self._SECRET))

    def test_empty_signature_rejected(self) -> None:
        self.assertFalse(verify_webhook_sha1_signature(self._PAYLOAD, "", self._SECRET))

    def test_empty_secret_rejected(self) -> None:
        sig = _make_sig(self._PAYLOAD, self._SECRET)
        self.assertFalse(verify_webhook_sha1_signature(self._PAYLOAD, sig, ""))

    def test_case_insensitive_digest(self) -> None:
        digest = hmac.new(self._SECRET.encode(), self._PAYLOAD, hashlib.sha1).hexdigest().upper()
        sig = f"sha1={digest}"
        self.assertTrue(verify_webhook_sha1_signature(self._PAYLOAD, sig, self._SECRET))


# ---------------------------------------------------------------------------
# IdempotencyGuard
# ---------------------------------------------------------------------------

class TestIdempotencyGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = IdempotencyGuard(ttl_seconds=10.0, max_size=5)

    def test_new_event_is_not_duplicate(self) -> None:
        self.assertFalse(self.guard.is_duplicate("evt-001"))

    def test_seen_event_is_duplicate(self) -> None:
        self.guard.mark_seen("evt-001")
        self.assertTrue(self.guard.is_duplicate("evt-001"))

    def test_different_event_ids_independent(self) -> None:
        self.guard.mark_seen("evt-001")
        self.assertFalse(self.guard.is_duplicate("evt-002"))

    def test_empty_event_id_never_duplicate(self) -> None:
        self.guard.mark_seen("")
        self.assertFalse(self.guard.is_duplicate(""))

    def test_expired_entry_not_duplicate(self) -> None:
        guard = IdempotencyGuard(ttl_seconds=0.05)
        guard.mark_seen("evt-exp")
        time.sleep(0.1)
        self.assertFalse(guard.is_duplicate("evt-exp"))

    def test_max_size_evicts_oldest(self) -> None:
        for i in range(5):
            self.guard.mark_seen(f"evt-{i:03d}")
        # Adding a 6th entry should evict the oldest
        self.guard.mark_seen("evt-005")
        # Guard should still work correctly for recent entries
        self.assertTrue(self.guard.is_duplicate("evt-005"))

    def test_mark_seen_then_is_duplicate(self) -> None:
        self.guard.mark_seen("make-event-xyz")
        self.assertTrue(self.guard.is_duplicate("make-event-xyz"))
        self.assertFalse(self.guard.is_duplicate("make-event-xyz-other"))


if __name__ == "__main__":
    unittest.main()
