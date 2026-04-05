"""Tests for PauBiometricInterface — biometric movement controller."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_biometric_interface import PauBiometricInterface


class TestPauBiometricInterfaceInit(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauBiometricInterface()

    def test_identity_is_real_white_peacock(self) -> None:
        self.assertEqual(self.pau.identity, "Real White Peacock - Natural")

    def test_states_contains_all_expected(self) -> None:
        expected = ["speaking", "laughing", "nodding", "tilting_head", "spreading_feathers"]
        self.assertEqual(self.pau.states, expected)

    def test_active_video_starts_none(self) -> None:
        self.assertIsNone(self.pau.active_video)

    def test_video_buffer_starts_empty(self) -> None:
        self.assertEqual(self.pau._video_buffer, {})

    def test_biometric_log_starts_empty(self) -> None:
        self.assertEqual(self.pau._biometric_log, [])


class TestLoadVideoBuffer(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauBiometricInterface()

    def test_returns_buffered_entry(self) -> None:
        movement = {"action": "speech_charisma", "beak_movement": "active", "expression": "elegant"}
        result = self.pau.load_video_buffer(movement)
        self.assertEqual(result["action"], "speech_charisma")
        self.assertEqual(result["status"], "buffered")

    def test_sets_active_video(self) -> None:
        movement = {"action": "speech_charisma", "beak_movement": "active"}
        self.pau.load_video_buffer(movement)
        self.assertIsNotNone(self.pau.active_video)
        self.assertEqual(self.pau.active_video["action"], "speech_charisma")

    def test_stores_in_buffer_by_action(self) -> None:
        movement = {"action": "joyful_laugh", "beak_movement": "slight_open"}
        self.pau.load_video_buffer(movement)
        self.assertIn("joyful_laugh", self.pau._video_buffer)

    def test_identity_embedded_in_buffer(self) -> None:
        movement = {"action": "approval_nod"}
        result = self.pau.load_video_buffer(movement)
        self.assertEqual(result["identity"], "Real White Peacock - Natural")

    def test_unknown_action_fallback(self) -> None:
        result = self.pau.load_video_buffer({})
        self.assertEqual(result["action"], "unknown")


class TestRenderInGoldenCoin(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauBiometricInterface()

    def test_frame_is_golden_coin(self) -> None:
        movement = {"action": "joyful_laugh", "beak_movement": "slight_open"}
        result = self.pau.render_in_golden_coin(movement)
        self.assertEqual(result["frame"], "golden_coin")

    def test_rendered_flag_is_true(self) -> None:
        movement = {"action": "majestic_posture", "neck_extension": "max"}
        result = self.pau.render_in_golden_coin(movement)
        self.assertTrue(result["rendered"])

    def test_action_preserved_in_result(self) -> None:
        movement = {"action": "curiosity_gesture", "head_tilt": "deep"}
        result = self.pau.render_in_golden_coin(movement)
        self.assertEqual(result["action"], "curiosity_gesture")

    def test_identity_embedded_in_render(self) -> None:
        movement = {"action": "approval_nod"}
        result = self.pau.render_in_golden_coin(movement)
        self.assertEqual(result["identity"], "Real White Peacock - Natural")

    def test_unknown_action_fallback(self) -> None:
        result = self.pau.render_in_golden_coin({})
        self.assertEqual(result["action"], "unknown")


class TestSyncBiometricData(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauBiometricInterface()

    def test_returns_synced_status(self) -> None:
        movement = {"action": "approval_nod", "head_movement": "vertical_slow", "gaze": "fixed_camera"}
        result = self.pau.sync_biometric_data(movement)
        self.assertEqual(result["status"], "synced")

    def test_action_stored_in_entry(self) -> None:
        movement = {"action": "curiosity_gesture", "head_tilt": "deep"}
        result = self.pau.sync_biometric_data(movement)
        self.assertEqual(result["action"], "curiosity_gesture")

    def test_params_exclude_action_key(self) -> None:
        movement = {"action": "speech_charisma", "beak_movement": "active", "expression": "elegant"}
        result = self.pau.sync_biometric_data(movement)
        self.assertNotIn("action", result["params"])
        self.assertEqual(result["params"]["beak_movement"], "active")
        self.assertEqual(result["params"]["expression"], "elegant")

    def test_appends_to_biometric_log(self) -> None:
        self.pau.sync_biometric_data({"action": "joyful_laugh"})
        self.pau.sync_biometric_data({"action": "approval_nod"})
        self.assertEqual(len(self.pau._biometric_log), 2)

    def test_identity_in_sync_entry(self) -> None:
        result = self.pau.sync_biometric_data({"action": "majestic_posture"})
        self.assertEqual(result["identity"], "Real White Peacock - Natural")


class TestExecuteMovementSequence(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauBiometricInterface()

    def test_all_five_movements_synced(self) -> None:
        self.pau.execute_movement_sequence()
        self.assertEqual(len(self.pau._biometric_log), 5)

    def test_all_expected_actions_present(self) -> None:
        self.pau.execute_movement_sequence()
        actions = [e["action"] for e in self.pau._biometric_log]
        for action in ("speech_charisma", "joyful_laugh", "approval_nod", "curiosity_gesture", "majestic_posture"):
            self.assertIn(action, actions)

    def test_active_video_set_after_sequence(self) -> None:
        self.pau.execute_movement_sequence()
        self.assertIsNotNone(self.pau.active_video)

    def test_all_five_actions_buffered(self) -> None:
        self.pau.execute_movement_sequence()
        self.assertEqual(len(self.pau._video_buffer), 5)

    def test_last_active_video_is_majestic_posture(self) -> None:
        self.pau.execute_movement_sequence()
        self.assertEqual(self.pau.active_video["action"], "majestic_posture")


if __name__ == "__main__":
    unittest.main()
