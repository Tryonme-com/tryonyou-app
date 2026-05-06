from __future__ import annotations

import asyncio
import importlib
import os
import unittest


class TestCompositeBunkerExecutor(unittest.TestCase):
    def test_module_imports_from_repo_root(self) -> None:
        module = importlib.import_module("composite_bunker_executor")
        self.assertTrue(hasattr(module, "CompositeBunker"))

    def test_process_lead_uses_stable_payload_without_webhook(self) -> None:
        module = importlib.import_module("composite_bunker_executor")
        captured: dict[str, object] = {}

        def fake_make(payload):
            captured["make_payload"] = payload
            return False

        def fake_waitlist(payload):
            captured["waitlist_payload"] = payload
            return True, "/tmp/leads_empire_waitlist.json"

        old_make = module._make_post_omega
        old_waitlist = module.append_waitlist_json
        module._make_post_omega = fake_make
        module.append_waitlist_json = fake_waitlist
        try:
            result = asyncio.run(
                module.CompositeBunker().process_lead(
                    email="vip@stationf.co",
                    revenue_eur=7_500.0,
                    days_delay=0,
                    extra_tags=["oberkampf_75011"],
                )
            )
        finally:
            module._make_post_omega = old_make
            module.append_waitlist_json = old_waitlist

        self.assertTrue(result.bpifrance_ok)
        self.assertTrue(result.waitlist_ok)
        self.assertEqual(result.waitlist_path, "/tmp/leads_empire_waitlist.json")
        payload = captured["waitlist_payload"]
        self.assertEqual(payload["event"], "omega_lead")
        self.assertEqual(payload["source"], "composite_bunker")
        self.assertIn("@stationf.co", payload["tags"])
        self.assertIn("oberkampf_75011", payload["tags"])
        self.assertIn("score", payload["vetos"])


class TestBunkerFullOrchestratorShim(unittest.TestCase):
    def test_optional_legacy_exports_do_not_break_import(self) -> None:
        module = importlib.import_module("bunker_full_orchestrator")
        self.assertIn("append_waitlist_json", module.__all__)
        self.assertFalse(
            hasattr(module, "BunkerOrchestrator"),
            "El shim no debe exigir exports legacy inexistentes.",
        )


if __name__ == "__main__":
    unittest.main()
