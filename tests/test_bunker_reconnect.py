"""Tests para el módulo logic/bunker_reconnect — Módulo de Reconexión V10.2."""

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
    SUCCESS_MESSAGE,
    BunkerControl,
    _DEFAULT_ACTION,
    _DEFAULT_TARGET,
    _STATUS_OK,
    _STATUS_RESET,
    main,
)


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
    def _run(self, **kwargs) -> tuple[str, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            ctrl = BunkerControl(**kwargs)
            result = ctrl.fix_sync()
        return result, buf.getvalue()

    def test_returns_success_message(self) -> None:
        result, _ = self._run(session="test-session")
        self.assertEqual(result, SUCCESS_MESSAGE)

    def test_status_updated_to_reconnected(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            ctrl = BunkerControl(session="test-session")
            ctrl.fix_sync()
        self.assertEqual(ctrl.status, _STATUS_OK)

    def test_output_contains_force_reset(self) -> None:
        _, output = self._run(session="abcdef12345")
        self.assertIn("FORCE RESET", output)

    def test_output_contains_session_preview(self) -> None:
        _, output = self._run(session="abcdef12345")
        self.assertIn("abcdef1", output)

    def test_output_contains_sincro(self) -> None:
        _, output = self._run(session="test-session")
        self.assertIn("SINCRO", output)

    def test_output_contains_estado(self) -> None:
        _, output = self._run(session="test-session")
        self.assertIn("ESTADO", output)

    def test_output_contains_target(self) -> None:
        _, output = self._run(session="test-session")
        self.assertIn(_DEFAULT_TARGET, output)

    def test_no_session_shows_na(self) -> None:
        old = os.environ.pop("BUNKER_SESSION_TOKEN", None)
        try:
            _, output = self._run()
            self.assertIn("N/A", output)
        finally:
            if old is not None:
                os.environ["BUNKER_SESSION_TOKEN"] = old


class TestBunkerControlBuildPayload(unittest.TestCase):
    def test_payload_has_correct_keys(self) -> None:
        ctrl = BunkerControl(session="s")
        payload = ctrl._build_payload()
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

    def test_payload_target_matches_instance_target(self) -> None:
        ctrl = BunkerControl(session="s", target="CustomTarget")
        payload = ctrl._build_payload()
        self.assertEqual(payload["target"], "CustomTarget")


class TestMain(unittest.TestCase):
    def test_main_returns_zero(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main()
        self.assertEqual(code, 0)

    def test_main_prints_success_message(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            main()
        self.assertIn(SUCCESS_MESSAGE, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
