"""Cobertura de salida para deploy_divineo.py (Protocolo OMEGA V10)."""

from __future__ import annotations

import io
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock

from deploy_divineo import PATENT, SOVEREIGN_PROTOCOL, deploy_divineo


class TestDeployDivineo(unittest.TestCase):
    def test_deploy_divineo_prints_full_final_block(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            deploy_divineo(nodes=("Core", "Security"), delay_seconds=0.0)

        output = buffer.getvalue()
        self.assertIn("INICIANDO DESPLIEGUE OMEGA", output)
        self.assertIn("Sincronizando Nodo CORE", output)
        self.assertIn("Sincronizando Nodo SECURITY", output)
        self.assertIn("PALOMA LAFAYETTE: SYNC COMPLETE", output)
        self.assertIn("GEMELO DIGITAL: 99.7% ACCURACY", output)
        self.assertIn("STATUS: VIVOS", output)
        self.assertIn(PATENT, output)
        self.assertIn(SOVEREIGN_PROTOCOL, output)

    def test_force_mode_sets_zero_delay(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = deploy_divineo(
                nodes=("Core",), delay_seconds=5.0, force=True,
            )
        output = buffer.getvalue()
        self.assertIn("FORCE MODE", output)
        self.assertTrue(result["deploy"])

    def test_sync_stripe_with_valid_key(self) -> None:
        env = {"STRIPE_SECRET_KEY": "sk_test_fake123"}
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with redirect_stdout(buffer):
                result = deploy_divineo(
                    nodes=("Core",), delay_seconds=0.0, sync_stripe=True,
                )
        output = buffer.getvalue()
        self.assertIn("STRIPE SYNC", output)
        self.assertTrue(result["deploy"])
        stripe_info = result["stripe"]
        self.assertTrue(stripe_info["ok"])

    def test_sync_stripe_missing_key_force(self) -> None:
        env = {"STRIPE_SECRET_KEY": ""}
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with redirect_stdout(buffer):
                result = deploy_divineo(
                    nodes=("Core",), delay_seconds=0.0,
                    sync_stripe=True, force=True,
                )
        output = buffer.getvalue()
        self.assertIn("STRIPE SYNC", output)
        self.assertIn("PALOMA LAFAYETTE: SYNC COMPLETE", output)

    def test_sync_stripe_missing_key_no_force_aborts(self) -> None:
        env = {"STRIPE_SECRET_KEY": ""}
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with redirect_stdout(buffer):
                result = deploy_divineo(
                    nodes=("Core",), delay_seconds=0.0,
                    sync_stripe=True, force=False,
                )
        self.assertFalse(result["deploy"])

    def test_apply_firestore_rules_present(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = deploy_divineo(
                nodes=("Core",), delay_seconds=0.0,
                apply_firestore_rules=True,
            )
        output = buffer.getvalue()
        self.assertIn("FIRESTORE RULES", output)
        self.assertTrue(result["deploy"])

    def test_apply_firestore_rules_force(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = deploy_divineo(
                nodes=("Core",), delay_seconds=0.0,
                apply_firestore_rules=True, force=True,
            )
        output = buffer.getvalue()
        self.assertIn("FIRESTORE RULES", output)
        self.assertIn("PALOMA LAFAYETTE: SYNC COMPLETE", output)

    def test_full_deploy_force_all_flags(self) -> None:
        """Simulates: python3 test_deploy_divineo.py --force --sync-stripe --apply-firestore-rules"""
        env = {"STRIPE_SECRET_KEY": "sk_test_omega"}
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with redirect_stdout(buffer):
                result = deploy_divineo(
                    delay_seconds=0.0,
                    force=True,
                    sync_stripe=True,
                    apply_firestore_rules=True,
                )
        output = buffer.getvalue()
        self.assertIn("FORCE MODE", output)
        self.assertIn("STRIPE SYNC", output)
        self.assertIn("FIRESTORE RULES", output)
        self.assertIn("PALOMA LAFAYETTE: SYNC COMPLETE", output)
        self.assertIn("GEMELO DIGITAL: 99.7% ACCURACY", output)
        self.assertIn("STATUS: VIVOS", output)
        self.assertIn(PATENT, output)
        self.assertIn(SOVEREIGN_PROTOCOL, output)
        self.assertTrue(result["deploy"])


if __name__ == "__main__":
    unittest.main()
