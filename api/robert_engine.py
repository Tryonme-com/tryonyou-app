from __future__ import annotations

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class RobertEngine:
    def __init__(self, model_asset_path: str = "pose_landmarker_heavy.task"):
        base_options = python.BaseOptions(model_asset_path=model_asset_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_poses=1,
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def process_frame(self, frame, timestamp_ms: int):
        """Inferencia de nodos biométricos con latencia objetivo sub-21.8ms."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        return self.landmarker.detect_for_video(mp_image, timestamp_ms)


robert_engine = RobertEngine()
