"""Tests para el modulo logic/bunker_reconnect - Modulo de Reconexion V10.2."""

from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_LOGIC = os.path.join(_ROOT, "logic")
for _p in (_ROOT, _LOGIC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bunker_reconnect import (
    BunkerControl,
    FAILURE_MESSAGE,
    SKIPPED_MESSAGE,
    SUCCESS_MESSAGE,
    _DEFAULT_ACTION,
    _DEFAULT_TARGET,
    _STATUS_FAILED,
    _STATUS_OK,
    _STATUS_PENDING_WEBHOOK,
    _STATUS_RESET,
    main,
    resolve_make_webhook_url,
)


class DummyResponse:
    def __init__(self, *, status_code: int = 200, ok: bool | None = None, text: str = "") -> None:
        self.status_code = status_code
        self.ok = 200 <= status_code < 300 if ok is None else ok
        self.text = text


class TestBunkerControlInit(unittest.TestCase):
    def test_default_status_is_resetting(self) -> None:
        ctrl = BunkerControl(session="abc123")
        self.assertEqual(ctrl.status, _STATUS_RESET)

    def test_session_is_stored(self) -> None:
        ctrl = BunkerControl(session="mysession")
        self.assertEqual(ctrl.session, "mysession")

    def test_default_target(self) -> None:
        ctrl = BunkerControl()
        self.assertEqual(ctrl.target, _DEFAULT_TARGET)

    def test_custom_target(self) -> None:
        ctrl = BunkerControl(target="MyCustomTarget")
        self.assertEqual(ctrl.target, "MyCustomTarget")

    def test_custom_webhook_url(self) -> None:
        ctrl = BunkerControl(webhook_url="https://hook.eu2.make.com/example")
        self.assertEqual(ctrl.webhook_url, "https://hook.eu2.make.com/example")

    def test_session_falls_back_to_env(self) -> None:
        old = os.environ.get("BUNKER_SESSION_TOKEN")
        os.environ["BUNKER_SESSION_TOKEN"] = "env-session-xyz"
        try:
            ctrl = BunkerControl()
            self.assertEqual(ctrl.session, "env-session-xyz")
        finally:
            if old is None:
                os.environ.pop("BUNKER_SESSION_TOKEN", None)
            else:
                os.environ["BUNKER_SESSION_TOKEN"] = old

    def test_explicit_session_overrides_env(self) -> None:
        old = os.environ.get("BUNKER_SESSION_TOKEN")
        os.environ["BUNKER_SESSION_TOKEN"] = "env-session-xyz"
        try:
            ctrl = BunkerControl(session="explicit-session")
            self.assertEqual(ctrl.session, "explicit-session")
        finally:
            if old is None:
                os.environ.pop("BUNKER_SESSION_TOKEN", None)
            else:
                os.environ["BUNKER_SESSION_TOKEN"] = old


class TestBunkerControlFixSync(unittest.TestCase):
    def _run(self, **kwargs) -> tuple[BunkerControl, str, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            ctrl = BunkerControl(**kwargs)
            result = ctrl.fix_sync()
        return ctrl, result, buf.getvalue()

    def test_returns_success_message(self) -> None:
        _, result, _ = self._run(
            session="test-session",
            webhook_url="https://hook.eu2.make.com/example",
            post=lambda *_args: DummyResponse(status_code=200),
        )
        self.assertEqual(result, SUCCESS_MESSAGE)

    def test_status_updated_to_reconnected(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            ctrl = BunkerControl(
                session="test-session",
                webhook_url="https://hook.eu2.make.com/example",
                post=lambda *_args: DummyResponse(status_code=204),
            )
            ctrl.fix_sync()
        self.assertEqual(ctrl.status, _STATUS_OK)

    def test_output_contains_force_reset(self) -> None:
        _, _, output = self._run(session="abcdef12345", webhook_url="")
        self.assertIn("FORCE RESET", output)

    def test_output_redacts_session_value(self) -> None:
        _, _, output = self._run(session="abcdef12345", webhook_url="")
        self.assertIn("REDACTED(len=11)", output)
        self.assertNotIn("abcdef", output)

    def test_output_contains_sincro(self) -> None:
        _, _, output = self._run(session="test-session", webhook_url="")
        self.assertIn("SINCRO", output)

    def test_output_contains_estado(self) -> None:
        _, _, output = self._run(session="test-session", webhook_url="")
        self.assertIn("ESTADO", output)

    def test_output_contains_target(self) -> None:
        _, _, output = self._run(session="test-session", webhook_url="")
        self.assertIn(_DEFAULT_TARGET, output)

    def test_no_session_shows_na(self) -> None:
        old = os.environ.pop("BUNKER_SESSION_TOKEN", None)
        try:
            _, _, output = self._run(webhook_url="")
            self.assertIn("N/A", output)
        finally:
            if old is not None:
                os.environ["BUNKER_SESSION_TOKEN"] = old

    def test_missing_webhook_is_safe_skip(self) -> None:
        ctrl, result, _ = self._run(session="test-session", webhook_url="")
        self.assertEqual(result, SKIPPED_MESSAGE)
        self.assertEqual(ctrl.status, _STATUS_PENDING_WEBHOOK)

    def test_posts_payload_when_webhook_is_configured(self) -> None:
        calls = []

        def post(url, payload, timeout):
            calls.append((url, payload, timeout))
            return DummyResponse(status_code=200)

        ctrl, result, _ = self._run(
            session="test-session",
            webhook_url="https://hook.eu2.make.com/example",
            post=post,
        )

        self.assertEqual(result, SUCCESS_MESSAGE)
        self.assertEqual(ctrl.status, _STATUS_OK)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "https://hook.eu2.make.com/example")
        self.assertEqual(calls[0][1]["action"], _DEFAULT_ACTION)

    def test_http_failure_is_reported(self) -> None:
        ctrl, result, _ = self._run(
            session="test-session",
            webhook_url="https://hook.eu2.make.com/example",
            post=lambda *_args: DummyResponse(status_code=500, text="boom"),
        )

        self.assertEqual(result, FAILURE_MESSAGE)
        self.assertEqual(ctrl.status, _STATUS_FAILED)
        self.assertEqual(ctrl.last_response_code, 500)


class TestBunkerControlBuildPayload(unittest.TestCase):
    def test_payload_has_correct_keys(self) -> None:
        ctrl = BunkerControl(session="s")
        payload = ctrl._build_payload()
        self.assertIn("event", payload)
        self.assertIn("target", payload)
        self.assertIn("action", payload)
        self.assertIn("pau_override", payload)

    def test_payload_action_is_clear_locks(self) -> None:
        ctrl = BunkerControl(session="s")
        payload = ctrl._build_payload()
        self.assertEqual(payload["action"], _DEFAULT_ACTION)

    def test_payload_pau_override_is_true(self) -> None:
        ctrl = BunkerControl(session="s")
        payload = ctrl._build_payload()
        self.assertIs(payload["pau_override"], True)

    def test_payload_records_session_presence_without_secret(self) -> None:
        ctrl = BunkerControl(session="secret-session")
        payload = ctrl._build_payload()
        self.assertIs(payload["session_present"], True)
        self.assertNotIn("secret-session", repr(payload))

    def test_payload_target_matches_instance_target(self) -> None:
        ctrl = BunkerControl(session="s", target="CustomTarget")
        payload = ctrl._build_payload()
        self.assertEqual(payload["target"], "CustomTarget")


class TestResolveMakeWebhookUrl(unittest.TestCase):
    def test_resolve_make_webhook_url_uses_first_configured_key(self) -> None:
        keys = (
            "MAKE_BUNKER_RECONNECT_WEBHOOK_URL",
            "MAKE_BUNKER_CONTROL_WEBHOOK_URL",
            "MAKE_WEBHOOK_URL",
        )
        old = {key: os.environ.get(key) for key in keys}
        for key in keys:
            os.environ.pop(key, None)
        os.environ["MAKE_BUNKER_CONTROL_WEBHOOK_URL"] = "https://hook.eu2.make.com/control"
        os.environ["MAKE_WEBHOOK_URL"] = "https://hook.eu2.make.com/generic"
        try:
            self.assertEqual(
                resolve_make_webhook_url(),
                "https://hook.eu2.make.com/control",
            )
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class TestMain(unittest.TestCase):
    def test_main_returns_zero(self) -> None:
        old = os.environ.pop("MAKE_BUNKER_RECONNECT_WEBHOOK_URL", None)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = main()
            self.assertEqual(code, 0)
        finally:
            if old is not None:
                os.environ["MAKE_BUNKER_RECONNECT_WEBHOOK_URL"] = old

    def test_main_prints_success_message(self) -> None:
        old = os.environ.pop("MAKE_BUNKER_RECONNECT_WEBHOOK_URL", None)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                main()
            self.assertIn(SKIPPED_MESSAGE, buf.getvalue())
        finally:
            if old is not None:
                os.environ["MAKE_BUNKER_RECONNECT_WEBHOOK_URL"] = old


if __name__ == "__main__":
    unittest.main()
