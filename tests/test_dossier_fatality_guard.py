"""Tests para dossier_fatality_guard."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dossier_fatality_guard import (
    REQUIRED_AMOUNT_CENTS,
    build_status,
    load_evidence,
    main,
    parse_instant,
    valid_confirmation_window,
)


class TestDossierFatalityGuard(unittest.TestCase):
    def test_valid_confirmation_window_requires_tuesday_08_utc(self) -> None:
        self.assertTrue(valid_confirmation_window(parse_instant("2026-05-05T08:00:00Z")))
        self.assertTrue(valid_confirmation_window(parse_instant("2026-05-05T08:59:59+00:00")))
        self.assertFalse(valid_confirmation_window(parse_instant("2026-05-04T08:00:00Z")))
        self.assertFalse(valid_confirmation_window(parse_instant("2026-05-05T09:00:00Z")))

    def test_missing_evidence_keeps_pending_validation(self) -> None:
        status = build_status(
            now=parse_instant("2026-05-05T08:00:00Z"),
            evidence={},
            confirmed_flag=True,
        )
        self.assertEqual(status["status"], "PENDING_VALIDATION")
        self.assertFalse(status["activated"])
        self.assertIn("evidence_missing", status["reasons"])

    def test_flag_is_required_even_with_valid_evidence(self) -> None:
        evidence = {
            "amount_cents": REQUIRED_AMOUNT_CENTS,
            "currency": "EUR",
            "source": "qonto",
            "reference": "qonto-operation-450k",
        }
        status = build_status(
            now=parse_instant("2026-05-05T08:00:00Z"),
            evidence=evidence,
            confirmed_flag=False,
        )
        self.assertEqual(status["status"], "PENDING_VALIDATION")
        self.assertIn("confirmation_flag_missing", status["reasons"])

    def test_valid_evidence_and_flag_activate_guard(self) -> None:
        evidence = {
            "amount_cents": REQUIRED_AMOUNT_CENTS,
            "currency": "EUR",
            "source": "bank",
            "reference": "bank-entry-450k",
        }
        status = build_status(
            now=parse_instant("2026-05-05T08:00:00Z"),
            evidence=evidence,
            confirmed_flag=True,
        )
        self.assertEqual(status["status"], "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(status["activated"])
        self.assertEqual(status["evidence"]["amount_cents"], REQUIRED_AMOUNT_CENTS)

    def test_load_evidence_rejects_invalid_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capital_450k_evidence.json"
            path.write_text("[1, 2, 3]", encoding="utf-8")
            self.assertEqual(load_evidence(path), {})

    def test_main_writes_json_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = Path(tmp) / "evidence.json"
            output_path = Path(tmp) / "status.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "amount_cents": REQUIRED_AMOUNT_CENTS,
                        "currency": "EUR",
                        "source": "qonto",
                        "reference": "qonto-op-1",
                    }
                ),
                encoding="utf-8",
            )
            env = {"TRYONYOU_CAPITAL_450K_CONFIRMED": "1", "SKIP_TELEGRAM": "1"}
            with patch.dict(os.environ, env, clear=False):
                code = main(
                    [
                        "--now",
                        "2026-05-05T08:00:00Z",
                        "--evidence",
                        str(evidence_path),
                        "--output",
                        str(output_path),
                        "--json",
                    ]
                )
            self.assertEqual(code, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "DOSSIER_FATALITY_ACTIVE")


if __name__ == "__main__":
    unittest.main()
