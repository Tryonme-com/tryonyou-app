from __future__ import annotations

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def _noop_result_callback(result, output_image, timestamp_ms) -> None:
    _ = (result, output_image, timestamp_ms)


def setup_pose_landmarker(model_asset_path: str = "pose_landmarker_heavy.task") -> vision.PoseLandmarker:
    """Configuración del landmarker optimizado para OMEGA."""
    base_options = python.BaseOptions(model_asset_path=model_asset_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True,
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=_noop_result_callback,
    )
    return vision.PoseLandmarker.create_from_options(options)


landmarker = setup_pose_landmarker()
