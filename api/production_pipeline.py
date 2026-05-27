from __future__ import annotations

from ar_engine import AR_Engine


def run_production_pipeline(frame, user_data):
    """Pipeline de producción: del escaneo al overlay."""
    engine = AR_Engine()
    nodes = user_data.extract_nodes()
    fit = user_data.calculate_fit()
    return engine.apply_biometric_overlay(frame, nodes, {"fit": fit})
