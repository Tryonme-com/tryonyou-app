"""
PauBiometricInterface — Real White Peacock biometric movement controller.

Manages movement sequences for the Pau peacock avatar:
  - Buffers video data per movement action.
  - Renders each movement inside the golden-coin display frame.
  - Synchronises biometric parameters (beak, head-tilt, gaze…) to the
    internal tracking log.
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class PauBiometricInterface:
    def __init__(self) -> None:
        self.identity = "Real White Peacock - Natural"
        self.states = ["speaking", "laughing", "nodding", "tilting_head", "spreading_feathers"]
        self.active_video: dict | None = None
        self._video_buffer: dict[str, dict] = {}
        self._biometric_log: list[dict] = []

    def execute_movement_sequence(self) -> None:
        """Execute the full canonical movement sequence for Pau."""
        movements = [
            {"action": "speech_charisma", "beak_movement": "active", "expression": "elegant"},
            {"action": "joyful_laugh", "beak_movement": "slight_open", "head_tilt": "lateral"},
            {"action": "approval_nod", "head_movement": "vertical_slow", "gaze": "fixed_camera"},
            {"action": "curiosity_gesture", "head_tilt": "deep", "blink_rate": "natural"},
            {"action": "majestic_posture", "neck_extension": "max", "stillness": "regal"},
        ]

        for move in movements:
            self.load_video_buffer(move)
            self.render_in_golden_coin(move)
            self.sync_biometric_data(move)

    def load_video_buffer(self, movement_data: dict) -> dict:
        """Load and prepare the video buffer for the given movement.

        Stores the buffer keyed by action name and updates ``active_video``.
        Returns the buffer entry so callers can inspect it.
        """
        action = movement_data.get("action", "unknown")
        buffer: dict = {
            "action": action,
            "identity": self.identity,
            "timestamp": time.time(),
            "data": movement_data,
            "status": "buffered",
        }
        self._video_buffer[action] = buffer
        self.active_video = buffer
        logger.debug("Video buffer loaded for action: %s", action)
        return buffer

    def render_in_golden_coin(self, movement_data: dict) -> dict:
        """Render the peacock movement inside the golden-coin display frame.

        Returns a render descriptor with frame metadata so the caller can
        forward it to any downstream display pipeline.
        """
        action = movement_data.get("action", "unknown")
        render_result: dict = {
            "frame": "golden_coin",
            "action": action,
            "identity": self.identity,
            "timestamp": time.time(),
            "rendered": True,
        }
        logger.debug("Rendered in golden coin frame: %s", action)
        return render_result

    def sync_biometric_data(self, movement_data: dict) -> dict:
        """Synchronise biometric movement parameters to the internal log.

        All keys except ``action`` are treated as biometric parameters and
        stored verbatim.  Returns the sync entry for inspection.
        """
        action = movement_data.get("action", "unknown")
        sync_entry: dict = {
            "identity": self.identity,
            "action": action,
            "synced_at": time.time(),
            "params": {k: v for k, v in movement_data.items() if k != "action"},
            "status": "synced",
        }
        self._biometric_log.append(sync_entry)
        logger.debug("Biometric data synced for action: %s", action)
        return sync_entry


if __name__ == "__main__":
    pau = PauBiometricInterface()
    pau.execute_movement_sequence()
