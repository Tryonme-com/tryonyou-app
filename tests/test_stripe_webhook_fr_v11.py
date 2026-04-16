from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from stripe_webhook_fr import process_stripe_webhook_event


class TestStripeWebhookFrV11(unittest.TestCase):
    def test_checkout_completed_paid_persists_and_notifies(self) -> None:
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "sess_paid_001",
                    "payment_status": "paid",
                    "amount_total": 1250000,
                    "metadata": {"session_id": "sess_paid_001"},
                }
            },
        }
        with (
            patch("stripe_webhook_fr._persist_sovereignty_state", return_value=True) as persist,
            patch("stripe_webhook_fr._notify_hito2_blindado") as notify,
        ):
            process_stripe_webhook_event(event)
        persist.assert_called_once()
        notify.assert_called_once_with(
            session_id="sess_paid_001",
            payment_status="paid",
            amount_eur=12500.0,
        )

    def test_checkout_completed_unpaid_skips_persist(self) -> None:
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "sess_open_001",
                    "payment_status": "open",
                    "amount_total": 1000,
                    "metadata": {},
                }
            },
        }
        with (
            patch("stripe_webhook_fr._persist_sovereignty_state") as persist,
            patch("stripe_webhook_fr._notify_hito2_blindado") as notify,
        ):
            process_stripe_webhook_event(event)
        persist.assert_not_called()
        notify.assert_not_called()

    def test_payment_intent_succeeded_uses_metadata_session_id(self) -> None:
        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_001",
                    "amount": 9900,
                    "currency": "eur",
                    "metadata": {"session_id": "sess_pi_001"},
                }
            },
        }
        with (
            patch("stripe_webhook_fr._persist_sovereignty_state", return_value=True) as persist,
            patch("stripe_webhook_fr._notify_hito2_blindado") as notify,
        ):
            process_stripe_webhook_event(event)
        persist.assert_called_once_with(
            session_id="sess_pi_001",
            payment_status="succeeded",
            amount_eur=99.0,
            metadata={"session_id": "sess_pi_001"},
        )
        notify.assert_called_once_with(
            session_id="sess_pi_001",
            payment_status="succeeded",
            amount_eur=99.0,
        )


class TestPersistSovereigntyStateV11(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = {
            "SUPABASE_URL": os.environ.get("SUPABASE_URL"),
            "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
            "CORE_ENGINE_USERS_TABLE": os.environ.get("CORE_ENGINE_USERS_TABLE"),
            "CORE_ENGINE_EVENTS_TABLE": os.environ.get("CORE_ENGINE_EVENTS_TABLE"),
        }
        os.environ["SUPABASE_URL"] = "https://example.supabase.co"
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "service-role-key"
        os.environ["CORE_ENGINE_USERS_TABLE"] = "users"
        os.environ["CORE_ENGINE_EVENTS_TABLE"] = "core_engine_events"

    def tearDown(self) -> None:
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_persist_updates_users_status_and_inserts_event(self) -> None:
        from stripe_webhook_fr import _persist_sovereignty_state

        calls: list[str] = []

        def _fake_urlopen(req, timeout=0):  # noqa: ANN001
            calls.append(f"{req.method} {req.full_url}")
            return object()

        with patch("stripe_webhook_fr.urllib.request.urlopen", side_effect=_fake_urlopen):
            ok = _persist_sovereignty_state(
                session_id="sess_42",
                payment_status="paid",
                amount_eur=12500.0,
                metadata={"a": 1},
            )

        self.assertTrue(ok)
        self.assertEqual(len(calls), 2)
        self.assertIn("PATCH https://example.supabase.co/rest/v1/users?session_id=eq.sess_42", calls[0])
        self.assertIn("POST https://example.supabase.co/rest/v1/core_engine_events", calls[1])


if __name__ == "__main__":
    unittest.main()
