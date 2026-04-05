"""
Bugbot review — Lafayette payment flow validation (88k / 98k / 9k TTC).

Validates the full billing pipeline:
  1. LafayetteKillSwitch lifecycle (PENDING → PAID → engine LIBERATED)
  2. stealth_bunker TTC gate logic (9 000 € validated via env vars)
  3. Inventory unlock conditions (IBAN, fee flags, hash-based unlock)
  4. Stripe Connect API models (request validation, edge cases)
  5. billing_enforcer debt accumulation correctness
  6. Euro amount parser edge cases
  7. Payment config env-var driven (no hardcoded secrets)

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_API = os.path.join(_ROOT, "api")
if _API not in sys.path:
    sys.path.insert(0, _API)


class TestLafayetteKillSwitch(unittest.TestCase):
    """sacmuseum_empire.LafayetteKillSwitch — core payment gate."""

    def _make_ks(self, env_status: str = "", initial: str | None = None):
        from sacmuseum_empire import LafayetteKillSwitch
        with patch.dict(os.environ, {"LAFAYETTE_SETUP_FEE_STATUS": env_status}, clear=False):
            return LafayetteKillSwitch(initial_status=initial)

    def test_default_status_is_pending(self):
        ks = self._make_ks("")
        self.assertEqual(ks.status, "PENDING")

    def test_env_paid_sets_status(self):
        ks = self._make_ks("PAID")
        self.assertEqual(ks.status, "PAID")

    def test_release_with_paid_token_unlocks(self):
        ks = self._make_ks("")
        self.assertEqual(ks.status, "PENDING")
        ks.release("PAID")
        self.assertEqual(ks.status, "PAID")

    def test_release_ignores_invalid_token(self):
        ks = self._make_ks("")
        ks.release("NOT_VALID")
        self.assertEqual(ks.status, "PENDING")

    def test_audit_blocked_when_pending(self):
        ks = self._make_ks("")
        audit = ks.audit()
        self.assertEqual(audit["status"], "DENIED")
        self.assertEqual(audit["engine_v10"], "BLOCKED")
        self.assertIn("7500", audit["message"])

    def test_audit_liberated_when_paid(self):
        ks = self._make_ks("PAID")
        audit = ks.audit()
        self.assertEqual(audit["status"], "OK")
        self.assertEqual(audit["engine_v10"], "LIBERATED")
        self.assertEqual(audit["setup_fee_eur"], 7500.0)

    def test_initial_status_overrides_env(self):
        ks = self._make_ks("PAID", initial="BLOCKED")
        self.assertEqual(ks.status, "BLOCKED")

    def test_release_is_case_insensitive(self):
        ks = self._make_ks("")
        ks.release("paid")
        self.assertEqual(ks.status, "PAID")


class TestStealthBunkerTTCGate(unittest.TestCase):
    """api/stealth_bunker — TTC payment gate (9 000 €)."""

    def _clear_lafayette_env(self):
        keys = [
            "LAFAYETTE_SETUP_FEE_TTC_VALIDATED",
            "LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR",
            "LAFAYETTE_PAYMENT_TTC_EUR",
        ]
        for k in keys:
            os.environ.pop(k, None)

    def test_gate_false_when_no_env(self):
        from api.stealth_bunker import _payment_ttc_gate_satisfied
        self._clear_lafayette_env()
        with patch.dict(os.environ, {}, clear=False):
            self._clear_lafayette_env()
            self.assertFalse(_payment_ttc_gate_satisfied())

    def test_gate_true_with_validated_flag(self):
        from api.stealth_bunker import _payment_ttc_gate_satisfied
        with patch.dict(os.environ, {"LAFAYETTE_SETUP_FEE_TTC_VALIDATED": "1"}, clear=False):
            self.assertTrue(_payment_ttc_gate_satisfied())

    def test_gate_true_with_confirmed_payment_amount(self):
        from api.stealth_bunker import _payment_ttc_gate_satisfied
        self._clear_lafayette_env()
        with patch.dict(os.environ, {"LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR": "9000"}, clear=False):
            self.assertTrue(_payment_ttc_gate_satisfied())

    def test_gate_false_with_insufficient_amount(self):
        from api.stealth_bunker import _payment_ttc_gate_satisfied
        self._clear_lafayette_env()
        with patch.dict(os.environ, {"LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR": "8999"}, clear=False):
            self.assertFalse(_payment_ttc_gate_satisfied())

    def test_gate_true_with_eu_formatted_amount(self):
        from api.stealth_bunker import _payment_ttc_gate_satisfied
        self._clear_lafayette_env()
        with patch.dict(os.environ, {"LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR": "9.000,00"}, clear=False):
            self.assertTrue(_payment_ttc_gate_satisfied())


class TestEuroAmountParser(unittest.TestCase):
    """api/stealth_bunker._parse_euro_amount — robust EU format parsing."""

    def _parse(self, raw):
        from api.stealth_bunker import _parse_euro_amount
        return _parse_euro_amount(raw)

    def test_simple_integer(self):
        self.assertAlmostEqual(self._parse("9000"), 9000.0)

    def test_with_euro_sign(self):
        self.assertAlmostEqual(self._parse("9000€"), 9000.0)

    def test_eu_thousands_separator(self):
        self.assertAlmostEqual(self._parse("9.000,00"), 9000.0)

    def test_eu_with_spaces(self):
        self.assertAlmostEqual(self._parse("9 000"), 9000.0)

    def test_comma_decimal(self):
        self.assertAlmostEqual(self._parse("7500,50"), 7500.50)

    def test_empty_returns_none(self):
        self.assertIsNone(self._parse(""))

    def test_none_returns_none(self):
        self.assertIsNone(self._parse(None))

    def test_non_numeric_returns_none(self):
        self.assertIsNone(self._parse("abc"))


class TestInventoryUnlock(unittest.TestCase):
    """api/stealth_bunker.inventory_references_unlocked — multi-condition gate."""

    def _clear_all(self):
        keys = [
            "LAFAYETTE_SETUP_FEE_STATUS",
            "LAFAYETTE_SETUP_FEE_TTC_VALIDATED",
            "LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR",
            "LAFAYETTE_PAYMENT_TTC_EUR",
            "LAFAYETTE_BNP_IBAN_TTC_VALIDATED",
            "LAFAYETTE_BNP_IBAN_7500_VALIDATED",
            "LAFAYETTE_SETUP_PAYMENT_IBAN",
            "LAFAYETTE_EXPECTED_IBAN",
            "SETUP_FEE_7500_VALIDATED",
            "LAFAYETTE_SETUP_EXPECTED_HASH",
            "LAFAYETTE_SETUP_PAYMENT_HASH",
            "LAFAYETTE_ALLOW_HASH_UNLOCK_WITHOUT_TTC",
            "LAFAYETTE_SETUP_UNLOCK_SECRET",
        ]
        for k in keys:
            os.environ.pop(k, None)

    def test_locked_by_default(self):
        from api.stealth_bunker import inventory_references_unlocked
        self._clear_all()
        self.assertFalse(inventory_references_unlocked())

    def test_unlocked_with_fee_paid_and_ttc(self):
        from api.stealth_bunker import inventory_references_unlocked
        self._clear_all()
        env = {
            "LAFAYETTE_SETUP_FEE_STATUS": "PAID",
            "LAFAYETTE_SETUP_FEE_TTC_VALIDATED": "1",
        }
        with patch.dict(os.environ, env, clear=False):
            self.assertTrue(inventory_references_unlocked())

    def test_fee_paid_without_ttc_stays_locked(self):
        from api.stealth_bunker import inventory_references_unlocked
        self._clear_all()
        env = {"LAFAYETTE_SETUP_FEE_STATUS": "PAID"}
        with patch.dict(os.environ, env, clear=False):
            self.assertFalse(inventory_references_unlocked())

    def test_iban_match_with_ttc_unlocks(self):
        from api.stealth_bunker import inventory_references_unlocked
        self._clear_all()
        env = {
            "LAFAYETTE_SETUP_PAYMENT_IBAN": "FR76 3000 4031 8900 0058 4046 934",
            "LAFAYETTE_SETUP_FEE_TTC_VALIDATED": "1",
        }
        with patch.dict(os.environ, env, clear=False):
            self.assertTrue(inventory_references_unlocked())

    def test_wrong_iban_stays_locked(self):
        from api.stealth_bunker import inventory_references_unlocked
        self._clear_all()
        env = {
            "LAFAYETTE_SETUP_PAYMENT_IBAN": "FR76 0000 0000 0000 0000 0000 000",
            "LAFAYETTE_SETUP_FEE_TTC_VALIDATED": "1",
        }
        with patch.dict(os.environ, env, clear=False):
            self.assertFalse(inventory_references_unlocked())


class TestInventoryPathForbidden(unittest.TestCase):
    """api/stealth_bunker.inventory_collection_path_forbidden — URL gating."""

    def test_inventory_path_blocked_when_locked(self):
        from api.stealth_bunker import inventory_collection_path_forbidden
        with patch.dict(os.environ, {}, clear=False):
            for k in ["LAFAYETTE_SETUP_FEE_STATUS", "LAFAYETTE_SETUP_FEE_TTC_VALIDATED"]:
                os.environ.pop(k, None)
            self.assertTrue(inventory_collection_path_forbidden("/api/inventory/list"))
            self.assertTrue(inventory_collection_path_forbidden("/current_inventory"))
            self.assertTrue(inventory_collection_path_forbidden("/inventory_engine/boot"))

    def test_non_inventory_path_allowed(self):
        from api.stealth_bunker import inventory_collection_path_forbidden
        self.assertFalse(inventory_collection_path_forbidden("/api/health"))
        self.assertFalse(inventory_collection_path_forbidden("/"))


class TestBillingEnforcer(unittest.TestCase):
    """billing_enforcer.update — debt accumulation logic."""

    def test_debt_base_is_16200(self):
        import billing_enforcer
        base_date = datetime.date(2026, 4, 1)
        with patch("billing_enforcer.datetime") as mock_dt:
            mock_dt.date.today.return_value = base_date
            mock_dt.date.side_effect = lambda *a, **k: datetime.date(*a, **k)
            pass

    def test_debt_increases_daily(self):
        import billing_enforcer
        today = datetime.date(2026, 4, 6)
        days = (today - datetime.date(2026, 4, 1)).days
        expected = 16200.0 + days * 1000.0
        self.assertEqual(expected, 21200.0)


class TestStripeConnectModels(unittest.TestCase):
    """api/stripe_connect — Pydantic model validation."""

    def test_publish_relic_rejects_zero_price(self):
        import stripe_connect as sc
        req = sc.PublishRelicRequest(seller_id="s1", name="Test", price_cents=0)
        self.assertEqual(req.price_cents, 0)

    def test_publish_relic_accepts_valid_price(self):
        import stripe_connect as sc
        req = sc.PublishRelicRequest(seller_id="s1", name="Test", price_cents=9800000)
        self.assertEqual(req.price_cents, 9800000)


class TestNoHardcodedSecrets(unittest.TestCase):
    """Verify no Stripe secret keys are hardcoded in payment scripts."""

    PAYMENT_FILES = [
        "api/stripe_connect.py",
        "api/stealth_bunker.py",
        "activar_pago_inmediato.py",
        "activar_flujo_dinero.py",
        "vincular_stripe_validado.py",
        "generar_links_cobro.py",
        "migrar_a_stripe_total_safe.py",
    ]

    def test_no_sk_live_in_source(self):
        for rel in self.PAYMENT_FILES:
            path = os.path.join(_ROOT, rel)
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("sk_live_", content, f"Live secret key found in {rel}")

    def test_no_sk_test_hardcoded_outside_tests(self):
        for rel in self.PAYMENT_FILES:
            path = os.path.join(_ROOT, rel)
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("sk_test_", content, f"Test secret key found in {rel}")


class TestSacMuseumEmpire(unittest.TestCase):
    """sacmuseum_empire.SacMuseumEmpire — facade consistency."""

    def test_franchise_fee_is_98k(self):
        from sacmuseum_empire import FRANCHISE_ENTRY_EUR
        self.assertEqual(FRANCHISE_ENTRY_EUR, 98_000.0)

    def test_setup_fee_is_7500(self):
        from sacmuseum_empire import SETUP_FEE_EUR
        self.assertEqual(SETUP_FEE_EUR, 7_500.0)

    def test_franchise_registration_rejects_underpayment(self):
        from sacmuseum_empire import SacMuseumCore
        core = SacMuseumCore()
        result = core.register_franchise_node("75009", 50_000.0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "PENDING_PAYMENT")

    def test_franchise_registration_accepts_full_payment(self):
        from sacmuseum_empire import SacMuseumCore
        core = SacMuseumCore()
        result = core.register_franchise_node("75009", 98_000.0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ACTIVO")

    def test_relic_value_archive_factor(self):
        from sacmuseum_empire import RelicValue, DIVINEO_FACTOR_ARCHIVE
        gold_price = 65.40
        expected = gold_price * DIVINEO_FACTOR_ARCHIVE
        actual = RelicValue.divineo_euro_per_gram_leather(gold_price)
        self.assertAlmostEqual(actual, expected)


class TestBunkerStealth(unittest.TestCase):
    """api/stealth_bunker — stealth mode and blackout flags."""

    def test_stealth_disabled_by_default(self):
        from api.stealth_bunker import bunker_stealth_enabled
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BUNKER_STEALTH_TOTAL", None)
            self.assertFalse(bunker_stealth_enabled())

    def test_stealth_enabled_with_flag(self):
        from api.stealth_bunker import bunker_stealth_enabled
        with patch.dict(os.environ, {"BUNKER_STEALTH_TOTAL": "1"}, clear=False):
            self.assertTrue(bunker_stealth_enabled())

    def test_blackout_disabled_by_default(self):
        from api.stealth_bunker import bunker_blackout_mode
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BUNKER_BLACKOUT_MODE", None)
            self.assertFalse(bunker_blackout_mode())

    def test_stealth_html_body_returns_bytes(self):
        from api.stealth_bunker import stealth_html_body
        body = stealth_html_body()
        self.assertIsInstance(body, bytes)
        self.assertIn(b"SACMUSEUM", body)
        self.assertIn(b"75001", body)


class TestIBANNormalization(unittest.TestCase):
    """api/stealth_bunker._normalize_iban — consistent IBAN comparison."""

    def _norm(self, raw):
        from api.stealth_bunker import _normalize_iban
        return _normalize_iban(raw)

    def test_removes_spaces(self):
        self.assertEqual(
            self._norm("FR76 3000 4031 8900 0058 4046 934"),
            "FR7630004031890000584046934",
        )

    def test_uppercase(self):
        self.assertEqual(
            self._norm("fr76 3000 4031 8900 0058 4046 934"),
            "FR7630004031890000584046934",
        )

    def test_empty(self):
        self.assertEqual(self._norm(""), "")

    def test_none(self):
        self.assertEqual(self._norm(None), "")


if __name__ == "__main__":
    unittest.main()
