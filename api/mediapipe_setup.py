from __future__ import annotations

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def setup_pose_landmarker(model_asset_path: str = "pose_landmarker_heavy.task") -> vision.PoseLandmarker:
    """Configuración del landmarker optimizado para OMEGA."""
    base_options = python.BaseOptions(model_asset_path=model_asset_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True,
        running_mode=vision.RunningMode.LIVE_STREAM,
    )
    return vision.PoseLandmarker.create_from_options(options)


landmarker = setup_pose_landmarker()
