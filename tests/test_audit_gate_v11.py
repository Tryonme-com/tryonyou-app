"""Puerta audit_log_v11 para finance_bridge."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_SCR = os.path.join(_ROOT, "scripts")
if _SCR not in sys.path:
    sys.path.insert(0, _SCR)

import importlib.util


def _load_audit_module():
    p = Path(_ROOT) / "scripts" / "parse_audit_log_v11.py"
    spec = importlib.util.spec_from_file_location("parse_audit_log_v11", p)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestAuditReconciliationMatched(unittest.TestCase):
    def test_explicit_line_matched(self) -> None:
        mod = _load_audit_module()
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("noise\nFINANCE_BRIDGE_AUDIT: MATCHED\n")
            path = f.name
        try:
            ok, reason = mod.audit_reconciliation_matched(path)
            self.assertTrue(ok)
            self.assertEqual(reason, "matched_marker_found")
        finally:
            os.unlink(path)

    def test_negative_overallocated(self) -> None:
        mod = _load_audit_module()
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("FINANCE_BRIDGE_AUDIT: MATCHED\nOVERALLOCATED_LEDGER\n")
            path = f.name
        try:
            ok, reason = mod.audit_reconciliation_matched(path)
            self.assertFalse(ok)
            self.assertEqual(reason, "negative_signal_in_log")
        finally:
            os.unlink(path)

    def test_json_ok(self) -> None:
        mod = _load_audit_module()
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write('{"reconciliation_status": "OK"}\n')
            path = f.name
        try:
            ok, reason = mod.audit_reconciliation_matched(path)
            self.assertTrue(ok)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
