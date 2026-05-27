from __future__ import annotations

from ar_engine import AR_Engine

_engine = AR_Engine()

def run_production_pipeline(frame, user_data):
    """Pipeline de producción: del escaneo al overlay."""
    nodes = user_data.extract_nodes()
    fit = user_data.calculate_fit()
    return _engine.apply_biometric_overlay(frame, nodes, {"fit": fit})
