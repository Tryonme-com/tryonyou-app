"""Pruebas del flujo Empire: intención de pago, éxito y trazabilidad/payout."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_API = _ROOT / "api"
for _p in (str(_ROOT), str(_API)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from api import index as api_index  # type: ignore
from empire_payout_trans import (
    TRACE_FILE_NAME,
    TRACE_REQUIRED_STEPS,
    get_flow_summary,
    register_checkout_success,
    register_payment_intent,
    register_payout_transition,
)


class TestEmpireTraceFlow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="tryonyou_empire_trace_")
        self.trace_dir = Path(self.tmp)
        os.environ["TRYONYOU_PAYMENT_TRACE_DIR"] = str(self.trace_dir)
        os.environ["TREASURY_PAYOUT_LOG_DIR"] = str(self.trace_dir / "treasury")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.environ.pop("TRYONYOU_PAYMENT_TRACE_DIR", None)
        os.environ.pop("TREASURY_PAYOUT_LOG_DIR", None)

    def _trace_path(self) -> Path:
        return self.trace_dir / TRACE_FILE_NAME

    def test_trace_detects_missing_steps(self) -> None:
        flow = "flow-missing"
        register_payment_intent(
            flow_token=flow,
            checkout_url="https://abvetos.com/checkout",
            button_id="tryonyou-pay-button",
            source="test",
            protocol="Pau Emotional Intelligence",
            ui_theme="Sello de Lujo: Antracita",
        )
        result = get_flow_summary(flow_token=flow)
        self.assertFalse(result["trace_integrity"])
        self.assertIn("checkout.session.completed", result["missing_steps"])

    def test_trace_complete_and_payout_registration(self) -> None:
        flow = "flow-ok"
        register_payment_intent(
            flow_token=flow,
            checkout_url="https://abvetos.com/checkout",
            button_id="tryonyou-pay-button",
            source="test",
            protocol="Pau Emotional Intelligence",
            ui_theme="Sello de Lujo: Antracita",
        )
        register_checkout_success(
            session_id="cs_live_ok",
            amount_total=10990000,
            currency="eur",
            customer_email="ops@tryonyou.fr",
            flow_token=flow,
            source="test",
        )

        trace_result = get_flow_summary(flow_token=flow)
        self.assertTrue(trace_result["trace_integrity"])
        self.assertEqual(len(trace_result["required_steps"]), len(TRACE_REQUIRED_STEPS))
        self.assertTrue(trace_result["payout_logged"])

    def test_manual_payout_transition_linked_to_flow(self) -> None:
        flow = "flow-manual-payout"
        register_payment_intent(
            flow_token=flow,
            checkout_url="https://abvetos.com/checkout",
            button_id="tryonyou-pay-button",
            source="test",
            protocol="Pau Emotional Intelligence",
            ui_theme="Sello de Lujo: Antracita",
        )
        register_payout_transition(
            amount_eur=489.0,
            recipient="Maison Divineo",
            concept="service_sanitation",
            flow_token=flow,
            session_id="po_manual_001",
            source="test_manual",
        )
        summary = get_flow_summary(flow_token=flow)
        self.assertTrue(summary["payout_logged"])
        self.assertFalse(summary["trace_integrity"])
        self.assertIn("checkout.session.completed", summary["missing_steps"])

    def test_api_endpoints_record_and_confirm_trace(self) -> None:
        client = api_index.app.test_client()
        flow = "flow-api"

        intent = client.post(
            "/api/v1/empire/payment-intent",
            json={
                "flow_token": flow,
                "checkout_url": "https://abvetos.com/checkout?variant=53412065182103",
                "button_id": "tryonyou-pay-button",
                "source": "index_html_shell",
            },
        )
        self.assertEqual(intent.status_code, 201)
        payload_intent = intent.get_json()
        self.assertEqual(payload_intent["status"], "ok")

        success = client.post(
            "/api/v1/empire/payment-success",
            json={
                "flow_token": flow,
                "session_id": "cs_live_flow_api",
                "amount_total": 10990000,
                "currency": "eur",
            },
        )
        self.assertEqual(success.status_code, 201)
        payload_success = success.get_json()
        self.assertEqual(payload_success["status"], "ok")
        self.assertEqual(payload_success["payment_success"]["checkout_success"]["souverainete_state"], 1)

        trace = client.get(f"/api/v1/empire/flow-status?flow_token={flow}")
        self.assertEqual(trace.status_code, 200)
        payload_trace = trace.get_json()
        self.assertEqual(payload_trace["status"], "ok")
        self.assertTrue(payload_trace["flow"]["trace_integrity"])

        trace_file = self._trace_path()
        self.assertTrue(trace_file.exists())
        lines = [line for line in trace_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(lines), 3)


if __name__ == "__main__":
    unittest.main()
