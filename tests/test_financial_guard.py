"""Tests FinancialGuard (402 en rutas de espejo sin QONTO)."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from financial_guard import (
    configure_boot_financial_guard,
    exit_after_mirror_402_enabled,
    is_mirror_request_path,
    qonto_pago_confirmado,
)


class TestFinancialGuardMiddleware(unittest.TestCase):
    def test_sovereignty_status_allowlisted_when_blocked(self) -> None:
        from flask import Flask

        from financial_guard import register_financial_guard_middleware

        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "FINANCIAL_GUARD_SKIP",
                "QONTO_BALANCE_EUR",
            )
        }
        try:
            os.environ["QONTO_BALANCE_EUR"] = "0"
            os.environ.pop("QONTO_PAGO_CONFIRMADO", None)
            app = Flask(__name__)

            @app.route("/api/sovereignty_guard_status", methods=["GET"])
            def _st():
                from financial_guard import sovereignty_status

                from flask import jsonify

                return jsonify(sovereignty_status()), 200

            register_financial_guard_middleware(app)
            c = app.test_client()
            r = c.get("/api/sovereignty_guard_status")
            self.assertEqual(r.status_code, 200)
            data = r.get_json()
            self.assertFalse(data.get("liquidity_ok"))
            self.assertTrue(data.get("sleep_mode"))
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_home_returns_402_when_blocked(self) -> None:
        from flask import Flask

        from financial_guard import register_financial_guard_middleware

        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "FINANCIAL_GUARD_SKIP",
                "QONTO_BALANCE_EUR",
            )
        }
        try:
            os.environ["QONTO_BALANCE_EUR"] = "0"
            os.environ.pop("QONTO_PAGO_CONFIRMADO", None)
            app = Flask(__name__)

            @app.route("/")
            def _home():
                return {"ok": True}

            register_financial_guard_middleware(app)
            c = app.test_client()
            r = c.get("/")
            self.assertEqual(r.status_code, 402)
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_mirror_returns_402_when_blocked(self) -> None:
        from flask import Flask

        from financial_guard import register_financial_guard_middleware

        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "FINANCIAL_GUARD_SKIP",
                "QONTO_BALANCE_EUR",
            )
        }
        old_exit = os.environ.get("FINANCIAL_GUARD_EXIT_AFTER_402")
        os.environ["FINANCIAL_GUARD_EXIT_AFTER_402"] = "0"
        try:
            os.environ["QONTO_BALANCE_EUR"] = "0"
            os.environ.pop("QONTO_PAGO_CONFIRMADO", None)
            os.environ.pop("FINANCIAL_GUARD_SKIP", None)
            app = Flask(__name__)

            @app.route("/api/mirror_digital_event", methods=["POST"])
            def _mirror():
                return {"ok": True}

            register_financial_guard_middleware(app)
            c = app.test_client()
            r = c.post("/api/mirror_digital_event", json={})
            self.assertEqual(r.status_code, 402)
            data = r.get_json()
            self.assertEqual(data.get("status"), "payment_required")
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            if old_exit is None:
                os.environ.pop("FINANCIAL_GUARD_EXIT_AFTER_402", None)
            else:
                os.environ["FINANCIAL_GUARD_EXIT_AFTER_402"] = old_exit

    def test_mirror_402_does_not_os_exit_when_exit_vars_unset(self) -> None:
        """Sin FINANCIAL_GUARD_EXIT_* el proceso no debe llamar os._exit tras 402 en mirror."""
        import time
        from unittest.mock import patch

        from flask import Flask

        from financial_guard import register_financial_guard_middleware

        keys = (
            "QONTO_PAGO_CONFIRMADO",
            "FINANCIAL_GUARD_SKIP",
            "QONTO_BALANCE_EUR",
            "FINANCIAL_GUARD_EXIT_AFTER_MIRROR_402",
            "FINANCIAL_GUARD_EXIT_AFTER_402",
        )
        old = {k: os.environ.pop(k, None) for k in keys}
        try:
            os.environ["QONTO_BALANCE_EUR"] = "0"
            app = Flask(__name__)

            @app.route("/api/mirror_digital_event", methods=["POST"])
            def _mirror():
                return {"ok": True}

            register_financial_guard_middleware(app)
            c = app.test_client()
            with patch("financial_guard.os._exit") as mock_exit:
                r = c.post("/api/mirror_digital_event", json={})
                self.assertEqual(r.status_code, 402)
                time.sleep(0.25)
            mock_exit.assert_not_called()
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class TestBootFinancialGuard(unittest.TestCase):
    def test_configure_boot_sets_config_liquidity_ok(self) -> None:
        from flask import Flask

        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "FINANCIAL_GUARD_SKIP",
                "QONTO_BALANCE_EUR",
                "FINANCIAL_GUARD_STRICT_BOOT",
            )
        }
        try:
            os.environ["QONTO_PAGO_CONFIRMADO"] = "1"
            app = Flask(__name__)
            configure_boot_financial_guard(app)
            self.assertTrue(app.config.get("FINANCIAL_GUARD_LIQUIDITY_OK"))
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_configure_boot_strict_exits_when_blocked(self) -> None:
        from flask import Flask

        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "FINANCIAL_GUARD_SKIP",
                "QONTO_BALANCE_EUR",
                "FINANCIAL_GUARD_STRICT_BOOT",
            )
        }
        try:
            os.environ["QONTO_BALANCE_EUR"] = "0"
            os.environ.pop("QONTO_PAGO_CONFIRMADO", None)
            os.environ["FINANCIAL_GUARD_STRICT_BOOT"] = "1"
            app = Flask(__name__)
            with self.assertRaises(SystemExit) as ctx:
                configure_boot_financial_guard(app)
            self.assertEqual(ctx.exception.code, 1)
            self.assertFalse(app.config.get("FINANCIAL_GUARD_LIQUIDITY_OK"))
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_configure_boot_non_strict_does_not_exit(self) -> None:
        from unittest.mock import patch

        from flask import Flask

        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "FINANCIAL_GUARD_SKIP",
                "QONTO_BALANCE_EUR",
                "FINANCIAL_GUARD_STRICT_BOOT",
            )
        }
        try:
            os.environ["QONTO_BALANCE_EUR"] = "0"
            os.environ.pop("QONTO_PAGO_CONFIRMADO", None)
            os.environ.pop("FINANCIAL_GUARD_STRICT_BOOT", None)
            app = Flask(__name__)
            with patch("financial_guard.sys.exit") as ex:
                configure_boot_financial_guard(app)
            ex.assert_not_called()
            self.assertFalse(app.config.get("FINANCIAL_GUARD_LIQUIDITY_OK"))
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class TestFinancialGuardHelpers(unittest.TestCase):
    def test_mirror_paths(self) -> None:
        self.assertTrue(is_mirror_request_path("/api/mirror_digital_event"))
        self.assertTrue(is_mirror_request_path("/api/mirror_shadow_log"))
        self.assertFalse(is_mirror_request_path("/api/stripe_inauguration_checkout"))

    def test_qonto_confirm_env(self) -> None:
        old = {
            k: os.environ.pop(k, None)
            for k in (
                "QONTO_PAGO_CONFIRMADO",
                "PAGO_CONFIRMADO_QONTO",
                "FINANCIAL_GUARD_SKIP",
            )
        }
        try:
            self.assertFalse(qonto_pago_confirmado())
            os.environ["QONTO_PAGO_CONFIRMADO"] = "false"
            self.assertFalse(qonto_pago_confirmado())
            os.environ["QONTO_PAGO_CONFIRMADO"] = "1"
            self.assertTrue(qonto_pago_confirmado())
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_exit_after_mirror_402_defaults_off(self) -> None:
        keys = (
            "FINANCIAL_GUARD_EXIT_AFTER_MIRROR_402",
            "FINANCIAL_GUARD_EXIT_AFTER_402",
        )
        old = {k: os.environ.pop(k, None) for k in keys}
        try:
            self.assertFalse(exit_after_mirror_402_enabled())
            os.environ["FINANCIAL_GUARD_EXIT_AFTER_402"] = "0"
            self.assertFalse(exit_after_mirror_402_enabled())
            os.environ["FINANCIAL_GUARD_EXIT_AFTER_402"] = "1"
            self.assertTrue(exit_after_mirror_402_enabled())
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


if __name__ == "__main__":
    unittest.main()
