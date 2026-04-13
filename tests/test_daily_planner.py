"""Tests for daily_planner.status_dia_10."""

from __future__ import annotations

import datetime
import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from daily_planner import OBJETIVO_BANCO, SIREN_REF, status_dia_10


def _fixed_dt(hour: int) -> datetime.datetime:
    """Return a real datetime with the given hour, created before any patching."""
    return datetime.datetime(2026, 4, 10, hour, 0, 0)


class TestStatusDia10BeforeNine(unittest.TestCase):
    """status_dia_10 when hour < 9 → ALERTA message."""

    def test_returns_alerta_at_hour_0(self) -> None:
        mock_now = _fixed_dt(0)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("ALERTA", result)

    def test_returns_alerta_at_hour_8(self) -> None:
        mock_now = _fixed_dt(8)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("ALERTA", result)

    def test_alerta_contains_objetivo(self) -> None:
        mock_now = _fixed_dt(7)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn(str(OBJETIVO_BANCO), result)

    def test_alerta_mentions_apertura_bancaria(self) -> None:
        mock_now = _fixed_dt(6)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("apertura bancaria", result)


class TestStatusDia10AfterNine(unittest.TestCase):
    """status_dia_10 when hour >= 9 → ACCIÓN message."""

    def test_returns_accion_at_hour_9(self) -> None:
        mock_now = _fixed_dt(9)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("ACCIÓN", result)

    def test_returns_accion_at_hour_12(self) -> None:
        mock_now = _fixed_dt(12)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("ACCIÓN", result)

    def test_returns_accion_at_hour_23(self) -> None:
        mock_now = _fixed_dt(23)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("ACCIÓN", result)

    def test_accion_mentions_banca_online(self) -> None:
        mock_now = _fixed_dt(10)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("banca online", result)

    def test_accion_mentions_clearing(self) -> None:
        mock_now = _fixed_dt(11)
        with patch("daily_planner.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            result = status_dia_10()
        self.assertIn("clearing", result)


class TestStatusDia10Constants(unittest.TestCase):
    def test_objetivo_banco_value(self) -> None:
        self.assertAlmostEqual(OBJETIVO_BANCO, 27500.00, places=2)

    def test_siren_ref_value(self) -> None:
        self.assertEqual(SIREN_REF, "943 610 196")

    def test_returns_string(self) -> None:
        result = status_dia_10()
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
