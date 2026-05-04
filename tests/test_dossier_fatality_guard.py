import json
import tempfile
import unittest
from pathlib import Path

from dossier_fatality_guard import evaluate_guard


class DossierFatalityGuardTests(unittest.TestCase):
    def test_requires_tuesday_eight_utc_window(self):
        result = evaluate_guard(
            now_value="2026-05-04T08:00:00+00:00",
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
            evidence_path=Path("/tmp/no-evidence.json"),
        )

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertIn("fuera de ventana", result.reason)

    def test_requires_confirmation_flag_before_evidence(self):
        result = evaluate_guard(
            now_value="2026-05-05T08:00:00+00:00",
            env={},
            evidence_path=Path("/tmp/no-evidence.json"),
        )

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertIn("TRYONYOU_CAPITAL_450K_CONFIRMED", result.reason)

    def test_requires_local_evidence_when_flag_is_present(self):
        result = evaluate_guard(
            now_value="2026-05-05T08:00:00+00:00",
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
            evidence_path=Path("/tmp/no-evidence.json"),
        )

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertIn("evidencia local ausente", result.reason)

    def test_activates_only_with_valid_bank_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_path = Path(tmpdir) / "capital_450k_evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "source": "Qonto",
                        "amount_cents": 45_000_000,
                        "currency": "EUR",
                        "reference": "QONTO-TRANSFER-450K",
                    }
                ),
                encoding="utf-8",
            )

            result = evaluate_guard(
                now_value="2026-05-05T08:00:00+00:00",
                env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
                evidence_path=evidence_path,
            )

        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertIn("capital 450000 EUR validado", result.reason)

    def test_environment_path_is_honored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_path = Path(tmpdir) / "capital_450k_evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "source": "bank",
                        "amount_cents": 45_000_000,
                        "currency": "EUR",
                        "reference": "BANK-TRANSFER-450K",
                    }
                ),
                encoding="utf-8",
            )
            env = {
                "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                "TRYONYOU_CAPITAL_EVIDENCE_PATH": str(evidence_path),
            }

            result = evaluate_guard(now_value="2026-05-05T08:00:00+00:00", env=env)

        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")


if __name__ == "__main__":
    unittest.main()
