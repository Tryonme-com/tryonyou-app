"""
Tests para FinalCommitModule — api/final_commit.py (unittest estándar).

Cubre:
  - commit_final: registro correcto, error sin SheetsBackend.
  - la_nina_perfecta_selection: delegación a agentes, registro, error sin deps.
  - final_snap: marcas integradas y no integradas, commit opcional.
  - send_final_qr: construcción de mensaje, URL QR, commit opcional, error sin MailService.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from final_commit import (
    DB_NAME,
    DIVINEO_LUXURY_BRANDS,
    PATENTE,
    QR_BASE_URL,
    SIREN,
    FinalCommitModule,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sheets() -> MagicMock:
    m = MagicMock()
    m.append_row = MagicMock()
    return m


def _make_agent(response: str = "mock-response") -> MagicMock:
    m = MagicMock()
    m.generate = MagicMock(return_value=response)
    return m


def _make_mail() -> MagicMock:
    m = MagicMock()
    m.send_raw = MagicMock()
    return m


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestModuleConstants(unittest.TestCase):
    def test_patente_value(self) -> None:
        self.assertEqual(PATENTE, "PCT/EP2025/067317")

    def test_siren_value(self) -> None:
        self.assertEqual(SIREN, "943 610 196")

    def test_luxury_brands_contains_balmain(self) -> None:
        self.assertIn("Balmain", DIVINEO_LUXURY_BRANDS)

    def test_luxury_brands_contains_chanel(self) -> None:
        self.assertIn("Chanel", DIVINEO_LUXURY_BRANDS)

    def test_luxury_brands_contains_dior(self) -> None:
        self.assertIn("Dior", DIVINEO_LUXURY_BRANDS)

    def test_luxury_brands_is_frozenset(self) -> None:
        self.assertIsInstance(DIVINEO_LUXURY_BRANDS, frozenset)

    def test_qr_base_url_contains_sacmuseum(self) -> None:
        self.assertIn("sacmuseum.app", QR_BASE_URL)

    def test_db_name_default(self) -> None:
        self.assertTrue(len(DB_NAME) > 0)


# ---------------------------------------------------------------------------
# commit_final
# ---------------------------------------------------------------------------


class TestCommitFinal(unittest.TestCase):
    def setUp(self) -> None:
        self.sheets = _make_sheets()
        self.mod = FinalCommitModule(sheets=self.sheets)

    def test_returns_dict(self) -> None:
        result = self.mod.commit_final("user@test.com", "TEST_ACTION", {"key": "val"})
        self.assertIsInstance(result, dict)

    def test_status_committed(self) -> None:
        result = self.mod.commit_final("user@test.com", "TEST_ACTION", {"key": "val"})
        self.assertEqual(result["status"], "COMMITTED")

    def test_user_id_preserved(self) -> None:
        result = self.mod.commit_final("alice@test.com", "ACT", {})
        self.assertEqual(result["user_id"], "alice@test.com")

    def test_action_preserved(self) -> None:
        result = self.mod.commit_final("u@t.com", "MY_ACTION", {})
        self.assertEqual(result["action"], "MY_ACTION")

    def test_result_preserved(self) -> None:
        payload = {"foo": 42}
        result = self.mod.commit_final("u@t.com", "A", payload)
        self.assertEqual(result["result"], payload)

    def test_timestamp_present(self) -> None:
        result = self.mod.commit_final("u@t.com", "A", {})
        self.assertIn("timestamp", result)

    def test_append_row_called_once(self) -> None:
        self.mod.commit_final("u@t.com", "A", {})
        self.sheets.append_row.assert_called_once()

    def test_append_row_has_five_fields(self) -> None:
        self.mod.commit_final("u@t.com", "A", {})
        row = self.sheets.append_row.call_args[0][0]
        self.assertEqual(len(row), 5)

    def test_append_row_last_field_committed(self) -> None:
        self.mod.commit_final("u@t.com", "A", {})
        row = self.sheets.append_row.call_args[0][0]
        self.assertEqual(row[-1], "COMMITTED")

    def test_raises_without_sheets(self) -> None:
        mod = FinalCommitModule()
        with self.assertRaises(RuntimeError):
            mod.commit_final("u@t.com", "A", {})

    def test_result_serializes_list(self) -> None:
        result = self.mod.commit_final("u@t.com", "A", [1, 2, 3])
        self.assertEqual(result["result"], [1, 2, 3])


# ---------------------------------------------------------------------------
# la_nina_perfecta_selection
# ---------------------------------------------------------------------------


class TestLaNinaPerfectaSelection(unittest.TestCase):
    def setUp(self) -> None:
        self.sheets = _make_sheets()
        self.agent_70 = _make_agent('{"items": ["dress1", "dress2"]}')
        self.jules = _make_agent("Presentación de Jules.")
        self.mod = FinalCommitModule(
            sheets=self.sheets,
            agent_70=self.agent_70,
            jules=self.jules,
        )

    def test_returns_dict(self) -> None:
        result = self.mod.la_nina_perfecta_selection(
            {"email": "test@test.com", "height": 170}, "Balmain"
        )
        self.assertIsInstance(result, dict)

    def test_selection_raw_from_agent_70(self) -> None:
        result = self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")
        self.assertEqual(result["selection_raw"], '{"items": ["dress1", "dress2"]}')

    def test_manifesto_from_jules(self) -> None:
        result = self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")
        self.assertEqual(result["manifesto"], "Presentación de Jules.")

    def test_commit_present(self) -> None:
        result = self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")
        self.assertIn("commit", result)
        self.assertIsNotNone(result["commit"])

    def test_commit_status_committed(self) -> None:
        result = self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")
        self.assertEqual(result["commit"]["status"], "COMMITTED")

    def test_commit_action_correct(self) -> None:
        result = self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")
        self.assertEqual(result["commit"]["action"], "LA_NINA_PERFECTA_EXEC")

    def test_agent_70_called_with_brand(self) -> None:
        self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Dior")
        prompt = self.agent_70.generate.call_args[0][0]
        self.assertIn("Dior", prompt)

    def test_jules_called_with_selection(self) -> None:
        self.mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")
        self.jules.generate.assert_called_once()

    def test_anonymous_user_when_no_email(self) -> None:
        result = self.mod.la_nina_perfecta_selection({}, "Balmain")
        self.assertEqual(result["commit"]["user_id"], "anonymous")

    def test_raises_without_agents(self) -> None:
        mod = FinalCommitModule(sheets=self.sheets)
        with self.assertRaises(RuntimeError):
            mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")

    def test_raises_without_sheets(self) -> None:
        mod = FinalCommitModule(agent_70=self.agent_70, jules=self.jules)
        with self.assertRaises(RuntimeError):
            mod.la_nina_perfecta_selection({"email": "t@t.com"}, "Balmain")


# ---------------------------------------------------------------------------
# final_snap
# ---------------------------------------------------------------------------


class TestFinalSnap(unittest.TestCase):
    def setUp(self) -> None:
        self.sheets = _make_sheets()
        self.mod = FinalCommitModule(sheets=self.sheets)

    def test_balmain_returns_la_nina_perfecta(self) -> None:
        result = self.mod.final_snap("Balmain", "user123")
        self.assertEqual(result["status"], "LA_NINA_PERFECTA")

    def test_chanel_returns_la_nina_perfecta(self) -> None:
        result = self.mod.final_snap("Chanel", "user123")
        self.assertEqual(result["status"], "LA_NINA_PERFECTA")

    def test_dior_returns_la_nina_perfecta(self) -> None:
        result = self.mod.final_snap("Dior", "user123")
        self.assertEqual(result["status"], "LA_NINA_PERFECTA")

    def test_unknown_brand_not_integrated(self) -> None:
        result = self.mod.final_snap("Zara", "user123")
        self.assertEqual(result["status"], "BRAND_NOT_INTEGRATED")

    def test_unknown_brand_message(self) -> None:
        result = self.mod.final_snap("Zara", "user123")
        self.assertEqual(result["message"], "Marca no integrada.")

    def test_luxury_brand_message_contains_brand(self) -> None:
        result = self.mod.final_snap("Balmain", "user123")
        self.assertIn("Balmain", result["message"])

    def test_luxury_brand_commit_created(self) -> None:
        result = self.mod.final_snap("Balmain", "user123")
        self.assertIsNotNone(result["commit"])
        self.assertEqual(result["commit"]["status"], "COMMITTED")

    def test_luxury_brand_commit_action(self) -> None:
        result = self.mod.final_snap("Balmain", "user123")
        self.assertEqual(result["commit"]["action"], "FINAL_SNAP")

    def test_unknown_brand_no_commit(self) -> None:
        result = self.mod.final_snap("Zara", "user123")
        self.assertIsNone(result["commit"])

    def test_legal_contains_patente(self) -> None:
        result = self.mod.final_snap("Balmain", "user123")
        self.assertIn(PATENTE, result["legal"])

    def test_legal_contains_siren(self) -> None:
        result = self.mod.final_snap("Balmain", "user123")
        self.assertIn(SIREN, result["legal"])

    def test_luxury_brand_no_sheets_no_commit(self) -> None:
        mod = FinalCommitModule()
        result = mod.final_snap("Balmain", "user123")
        self.assertIsNone(result["commit"])
        self.assertEqual(result["status"], "LA_NINA_PERFECTA")

    def test_sheets_not_called_for_unknown_brand(self) -> None:
        self.mod.final_snap("Gucci", "user123")
        self.sheets.append_row.assert_not_called()

    def test_sheets_called_once_for_luxury_brand(self) -> None:
        self.mod.final_snap("Chanel", "user123")
        self.sheets.append_row.assert_called_once()


# ---------------------------------------------------------------------------
# send_final_qr
# ---------------------------------------------------------------------------


class TestSendFinalQr(unittest.TestCase):
    def setUp(self) -> None:
        self.sheets = _make_sheets()
        self.mail = _make_mail()
        self.mod = FinalCommitModule(sheets=self.sheets, mail=self.mail)

    def test_returns_dict(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertIsInstance(result, dict)

    def test_status_qr_sent(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertEqual(result["status"], "QR_SENT")

    def test_email_preserved(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertEqual(result["email"], "alice@test.com")

    def test_look_id_preserved(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertEqual(result["look_id"], "LOOK-001")

    def test_qr_url_contains_look_id(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-XYZ")
        self.assertIn("LOOK-XYZ", result["qr_url"])

    def test_qr_url_contains_sacmuseum(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertIn("sacmuseum.app", result["qr_url"])

    def test_mail_send_raw_called_once(self) -> None:
        self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.mail.send_raw.assert_called_once()

    def test_mail_raw_is_string(self) -> None:
        self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        raw = self.mail.send_raw.call_args[0][0]
        self.assertIsInstance(raw, str)

    def test_commit_created_with_sheets(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertIsNotNone(result["commit"])
        self.assertEqual(result["commit"]["status"], "COMMITTED")

    def test_commit_action_qr_sent(self) -> None:
        result = self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertEqual(result["commit"]["action"], "QR_FINAL_SENT")

    def test_commit_none_without_sheets(self) -> None:
        mod = FinalCommitModule(mail=self.mail)
        result = mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        self.assertIsNone(result["commit"])

    def test_raises_without_mail(self) -> None:
        mod = FinalCommitModule(sheets=self.sheets)
        with self.assertRaises(RuntimeError):
            mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")

    def test_raw_message_base64_decodeable(self) -> None:
        import base64

        self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        raw = self.mail.send_raw.call_args[0][0]
        decoded = base64.urlsafe_b64decode(raw + "==")
        self.assertIsInstance(decoded, bytes)

    def _decode_mime_body(self, raw: str) -> str:
        """Decodes the Gmail API raw message (outer base64) and extracts the MIME body."""
        import base64
        import email as email_lib

        outer = base64.urlsafe_b64decode(raw + "==")
        msg = email_lib.message_from_bytes(outer)
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            return payload.decode("utf-8", errors="replace")
        # Fallback: return raw decoded string if payload is already a string
        return str(payload)

    def test_decoded_message_contains_recipient_name(self) -> None:
        self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-001")
        raw = self.mail.send_raw.call_args[0][0]
        body = self._decode_mime_body(raw)
        self.assertIn("Alice", body)

    def test_decoded_message_contains_look_id(self) -> None:
        self.mod.send_final_qr("alice@test.com", "Alice", "LOOK-007")
        raw = self.mail.send_raw.call_args[0][0]
        body = self._decode_mime_body(raw)
        self.assertIn("LOOK-007", body)


if __name__ == "__main__":
    unittest.main()
