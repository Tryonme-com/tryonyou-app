"""Tests for daily_planner module."""

from __future__ import annotations

import datetime
import os
import sys
import unittest
from unittest.mock import Mock, patch

import requests

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from daily_planner import (
    DEPLOY_BOT_NAME,
    HORA_DOSSIER_FATALITY,
    OBJETIVO_BANCO,
    OBJETIVO_CAPITAL_EUR,
    SIREN_REF,
    enviar_notificacion_exito,
    ejecutar_supercommit_max,
    status_dia_10,
)


def _fixed_dt(year: int, month: int, day: int, hour: int) -> datetime.datetime:
    """Return a real datetime with the given date and hour."""
    return datetime.datetime(year, month, day, hour, 0, 0)


class TestStatusDia10RegularSchedule(unittest.TestCase):
    """status_dia_10 for non-Tuesday routine schedule."""

    def test_returns_alerta_before_nine(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 8))
        self.assertIn("ALERTA", result)

    def test_alerta_contains_objetivo_banco(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 7))
        self.assertIn(str(OBJETIVO_BANCO), result)

    def test_alerta_mentions_apertura_bancaria(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 6))
        self.assertIn("apertura bancaria", result)

    def test_returns_accion_after_nine(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 12))
        self.assertIn("ACCIÓN", result)

    def test_accion_mentions_banca_online(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 10))
        self.assertIn("banca online", result)

    def test_accion_mentions_clearing(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 11))
        self.assertIn("clearing", result)


class TestStatusDia10TuesdaySecurity(unittest.TestCase):
    """Tuesday-specific security flow around 08:00."""

    def test_tuesday_pre_0800_requires_preparation(self) -> None:
        # 2026-04-14 is Tuesday
        result = status_dia_10(_fixed_dt(2026, 4, 14, HORA_DOSSIER_FATALITY - 1))
        self.assertIn("Martes pre-08:00", result)
        self.assertIn("Dossier Fatality", result)

    def test_tuesday_0800_or_later_requires_activation(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 14, HORA_DOSSIER_FATALITY))
        self.assertIn("SEGURIDAD", result)
        self.assertIn("Dossier Fatality", result)
        self.assertIn("450.000,00", result)


class TestStatusDia10Constants(unittest.TestCase):
    def test_objetivo_banco_value(self) -> None:
        self.assertAlmostEqual(OBJETIVO_BANCO, 27500.00, places=2)

    def test_objetivo_capital_value(self) -> None:
        self.assertAlmostEqual(OBJETIVO_CAPITAL_EUR, 450000.00, places=2)

    def test_siren_ref_value(self) -> None:
        self.assertEqual(SIREN_REF, "943 610 196")

    def test_hora_dossier_fatality_value(self) -> None:
        self.assertEqual(HORA_DOSSIER_FATALITY, 8)

    def test_returns_string(self) -> None:
        result = status_dia_10(_fixed_dt(2026, 4, 10, 9))
        self.assertIsInstance(result, str)


class TestEnviarNotificacionExito(unittest.TestCase):
    def test_returns_false_without_token_or_chat(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = enviar_notificacion_exito("ok")
        self.assertFalse(result)

    def test_sends_notification_with_bot_name_prefix(self) -> None:
        with patch.dict(
            os.environ,
            {"TRYONYOU_DEPLOY_BOT_TOKEN": "token-demo", "TRYONYOU_DEPLOY_CHAT_ID": "12345"},
            clear=True,
        ):
            with patch("daily_planner.requests.post") as mock_post:
                mock_post.return_value = Mock(status_code=200)
                result = enviar_notificacion_exito("despliegue correcto")

        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        self.assertIn("token-demo", args[0])
        self.assertEqual(kwargs["json"]["chat_id"], "12345")
        self.assertTrue(kwargs["json"]["text"].startswith(DEPLOY_BOT_NAME))

    def test_returns_false_when_telegram_raises(self) -> None:
        with patch.dict(
            os.environ,
            {"TRYONYOU_DEPLOY_BOT_TOKEN": "token-demo", "TRYONYOU_DEPLOY_CHAT_ID": "12345"},
            clear=True,
        ):
            with patch(
                "daily_planner.requests.post",
                side_effect=requests.RequestException("network"),
            ):
                result = enviar_notificacion_exito("despliegue correcto")
        self.assertFalse(result)


class TestEjecutarSupercommitMax(unittest.TestCase):
    def test_returns_syntax_failure_code(self) -> None:
        with patch("daily_planner.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=2)
            rc = ejecutar_supercommit_max()

        self.assertEqual(rc, 2)
        self.assertEqual(mock_run.call_count, 1)
        command = mock_run.call_args.args[0]
        self.assertEqual(command[:2], ["bash", "-n"])
        self.assertIn("supercommit_max.sh", command[2])

    def test_executes_script_after_passing_syntax(self) -> None:
        with patch("daily_planner.subprocess.run") as mock_run:
            mock_run.side_effect = [Mock(returncode=0), Mock(returncode=0)]
            rc = ejecutar_supercommit_max(["--fast"])

        self.assertEqual(rc, 0)
        self.assertEqual(mock_run.call_count, 2)
        execute_cmd = mock_run.call_args_list[1].args[0]
        self.assertEqual(execute_cmd[:2], ["bash", execute_cmd[1]])
        self.assertIn("--fast", execute_cmd)


if __name__ == "__main__":
    unittest.main()
