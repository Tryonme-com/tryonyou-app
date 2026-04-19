"""Tests para BUNKER_AUTO_PILOT.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from BUNKER_AUTO_PILOT import AutonomousEmpire, PilotConfig


def _cfg() -> PilotConfig:
    return PilotConfig(
        github_repo="tryonme-com/tryonyou-app",
        github_token="ghs_test",
        telegram_token="tg_test",
        telegram_chat_id="@tryonyou_deploy_bot",
        render_health_url="https://render.example/health",
        stripe_webhook_health_url="https://stripe.example/webhook-health",
        financial_impact_eur=51988.50,
        capital_entry_target_eur=450000.0,
        capital_entry_confirmed=True,
        timezone_name="Europe/Paris",
        supercommit_fast_mode=False,
        supercommit_message="sync bunker",
    )


class TestTargetPR(unittest.TestCase):
    def test_target_by_title_keyword(self) -> None:
        pilot = AutonomousEmpire(_cfg())
        pr = {"number": 11, "title": "Conexión Bancaria para piloto", "body": ""}
        self.assertTrue(pilot._target_pr(pr))

    def test_target_by_number(self) -> None:
        pilot = AutonomousEmpire(_cfg())
        pr = {"number": 182, "title": "Sin keyword", "body": ""}
        self.assertTrue(pilot._target_pr(pr))

    def test_non_target(self) -> None:
        pilot = AutonomousEmpire(_cfg())
        pr = {"number": 99, "title": "Refactor UI", "body": "sin temas financieros"}
        self.assertFalse(pilot._target_pr(pr))


class TestSecurityRoutine(unittest.TestCase):
    def test_activate_dossier_fatality_creates_artifact(self) -> None:
        pilot = AutonomousEmpire(_cfg())
        with tempfile.TemporaryDirectory() as tmp:
            pilot.repo_root = Path(tmp)
            now = __import__("datetime").datetime(2026, 4, 14, 8, 0, 0)
            ok, detail = pilot._activate_dossier_fatality(now)
            self.assertTrue(ok)
            self.assertIn("Dossier Fatality activado", detail)
            artifact = Path(tmp) / "dossier_fatality_activation.json"
            self.assertTrue(artifact.is_file())

    def test_activate_dossier_fatality_requires_exact_450k(self) -> None:
        cfg = _cfg()
        cfg = PilotConfig(
            github_repo=cfg.github_repo,
            github_token=cfg.github_token,
            telegram_token=cfg.telegram_token,
            telegram_chat_id=cfg.telegram_chat_id,
            render_health_url=cfg.render_health_url,
            stripe_webhook_health_url=cfg.stripe_webhook_health_url,
            financial_impact_eur=cfg.financial_impact_eur,
            capital_entry_target_eur=449999.0,
            capital_entry_confirmed=True,
            timezone_name=cfg.timezone_name,
            supercommit_fast_mode=cfg.supercommit_fast_mode,
            supercommit_message=cfg.supercommit_message,
        )
        pilot = AutonomousEmpire(cfg)
        with tempfile.TemporaryDirectory() as tmp:
            pilot.repo_root = Path(tmp)
            now = __import__("datetime").datetime(2026, 4, 14, 8, 0, 0)
            ok, detail = pilot._activate_dossier_fatality(now)
            self.assertFalse(ok)
            self.assertIn("450000.00", detail)

    @patch.object(AutonomousEmpire, "_telegram_report")
    @patch.object(AutonomousEmpire, "_activate_dossier_fatality")
    @patch.object(AutonomousEmpire, "_is_tuesday_0800")
    def test_security_routine_reports_when_window_matches(
        self,
        mock_is_tuesday: object,
        mock_activate: object,
        mock_telegram: object,
    ) -> None:
        pilot = AutonomousEmpire(_cfg())
        mock_is_tuesday.return_value = True
        mock_activate.return_value = (True, "Dossier Fatality activado")

        pilot._security_routine()

        self.assertTrue(mock_activate.called)
        self.assertTrue(mock_telegram.called)


class TestProcessPR(unittest.TestCase):
    @patch.object(AutonomousEmpire, "_telegram_report")
    @patch.object(AutonomousEmpire, "_merge_pr")
    @patch.object(AutonomousEmpire, "_bash_syntax_check")
    @patch.object(AutonomousEmpire, "_run_supercommit_max")
    @patch.object(AutonomousEmpire, "_validate_stripe_webhooks")
    @patch.object(AutonomousEmpire, "_validate_render")
    def test_process_pr_merges_when_all_checks_ok(
        self,
        mock_render: object,
        mock_stripe: object,
        mock_supercommit: object,
        mock_bash: object,
        mock_merge: object,
        mock_tg: object,
    ) -> None:
        pilot = AutonomousEmpire(_cfg())
        mock_render.return_value = (True, "ok")
        mock_stripe.return_value = (True, "ok")
        mock_supercommit.return_value = (True, "ok")
        mock_bash.return_value = (True, "ok")
        mock_merge.return_value = (True, "merged")

        pilot._process_pr({"number": 187, "title": "Conexión Bancaria", "body": ""})

        self.assertTrue(mock_merge.called)
        self.assertTrue(mock_tg.called)

    @patch.object(AutonomousEmpire, "_merge_pr")
    @patch.object(AutonomousEmpire, "_bash_syntax_check")
    @patch.object(AutonomousEmpire, "_run_supercommit_max")
    @patch.object(AutonomousEmpire, "_validate_stripe_webhooks")
    @patch.object(AutonomousEmpire, "_validate_render")
    def test_process_pr_no_merge_if_any_check_fails(
        self,
        mock_render: object,
        mock_stripe: object,
        mock_supercommit: object,
        mock_bash: object,
        mock_merge: object,
    ) -> None:
        pilot = AutonomousEmpire(_cfg())
        mock_render.return_value = (False, "render down")
        mock_stripe.return_value = (True, "ok")
        mock_supercommit.return_value = (True, "ok")
        mock_bash.return_value = (True, "ok")

        pilot._process_pr({"number": 182, "title": "Settlement", "body": ""})

        self.assertFalse(mock_merge.called)


if __name__ == "__main__":
    unittest.main()
