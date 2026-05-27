from __future__ import annotations

import logging
from typing import Any


def certify_render_pipeline(frame: Any, overlay_status: bool) -> bool:
    """Certificación de integridad del pipeline de renderizado."""
    if frame is not None and overlay_status:
        logging.info("Certificación: Overlay inyectado correctamente en el frame.")
        return True

    logging.error("Fallo de certificación: El pipeline de renderizado no está inyectando la capa.")
    return False
