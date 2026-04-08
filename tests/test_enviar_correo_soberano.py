"""Tests for enviar_correo_soberano — including the Aubenard Legal V9 template."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from enviar_correo_soberano import (
    _SUBJECT_AUBENARD_V9,
    cuerpo_aubenard_legal_v9,
    enviar_correo_soberano,
)


class TestSubjectAubenardV9(unittest.TestCase):
    def test_subject_contains_estrategia_legal_v9(self) -> None:
        self.assertIn("ESTRATEGIA LEGAL V9", _SUBJECT_AUBENARD_V9)

    def test_subject_contains_propuesta_licenciamiento(self) -> None:
        self.assertIn("PROPUESTA DE LICENCIAMIENTO", _SUBJECT_AUBENARD_V9)

    def test_subject_contains_acuerdo_amigable(self) -> None:
        self.assertIn("ACUERDO AMIGABLE", _SUBJECT_AUBENARD_V9)


class TestCuerpoAubenardLegalV9(unittest.TestCase):
    def setUp(self) -> None:
        self.body = cuerpo_aubenard_legal_v9()

    def test_addressee_is_aubenard(self) -> None:
        self.assertIn("Aubenard", self.body)

    def test_mentions_fase_inicial(self) -> None:
        self.assertIn("FASE INICIAL", self.body)

    def test_mentions_snap_to_look(self) -> None:
        self.assertIn("Snap-to-Look", self.body)

    def test_mentions_zero_size_engine(self) -> None:
        self.assertIn("Zero Size Engine", self.body)

    def test_mentions_royalties_v10(self) -> None:
        self.assertIn("Sistema de Royalties V10", self.body)

    def test_mentions_20_entidades(self) -> None:
        self.assertIn("20 entidades infractoras", self.body)

    def test_signed_by_founder(self) -> None:
        self.assertIn("Rubén Espinar", self.body)
        self.assertIn("Fundador", self.body)

    def test_returns_string(self) -> None:
        self.assertIsInstance(self.body, str)

    def test_body_is_not_empty(self) -> None:
        self.assertTrue(len(self.body) > 100)


class TestEnviarCorreoSoberanoAubenardDryRun(unittest.TestCase):
    """Verifies that dry_run mode works for the Aubenard V9 dispatch."""

    def test_dry_run_returns_true_with_creds(self) -> None:
        with patch.dict(
            os.environ,
            {"EMAIL_USER": "test@example.com", "EMAIL_PASS": "test_pass"},
        ):
            result = enviar_correo_soberano(
                "Contact@aubenard.fr",
                _SUBJECT_AUBENARD_V9,
                cuerpo_aubenard_legal_v9(),
                dry_run=True,
            )
        self.assertTrue(result)

    def test_dry_run_returns_false_without_user(self) -> None:
        env = {k: v for k, v in os.environ.items() if k not in (
            "EMAIL_USER", "E50_SMTP_USER", "FOUNDER_EMAIL",
            "EMAIL_PASS", "E50_SMTP_PASS",
        )}
        with patch.dict(os.environ, env, clear=True):
            result = enviar_correo_soberano(
                "Contact@aubenard.fr",
                _SUBJECT_AUBENARD_V9,
                cuerpo_aubenard_legal_v9(),
                dry_run=True,
            )
        self.assertFalse(result)

    def test_dry_run_returns_false_without_pass(self) -> None:
        env = {k: v for k, v in os.environ.items() if k not in (
            "EMAIL_PASS", "E50_SMTP_PASS",
        )}
        env["EMAIL_USER"] = "test@example.com"
        with patch.dict(os.environ, env, clear=True):
            result = enviar_correo_soberano(
                "Contact@aubenard.fr",
                _SUBJECT_AUBENARD_V9,
                cuerpo_aubenard_legal_v9(),
                dry_run=True,
            )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
