"""
Compatibilidad: el módulo canónico vive en ``api/bunker_full_orchestrator.py``.
Los imports ``from bunker_full_orchestrator import …`` siguen funcionando cuando
el directorio ``api/`` precede a la raíz en ``sys.path`` (p. ej. ``api/index.py``),
o vía este shim cuando se importa desde la raíz del repo.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_impl_path = Path(__file__).resolve().parent / "api" / "bunker_full_orchestrator.py"
_spec = importlib.util.spec_from_file_location(
    "bunker_full_orchestrator_impl",
    _impl_path,
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"No se pudo cargar {_impl_path}")

_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

VETOS_PRIORITY_BETA = _mod.VETOS_PRIORITY_BETA
append_waitlist_json = _mod.append_waitlist_json
orchestrate_beta_waitlist = _mod.orchestrate_beta_waitlist
orchestrate_bunker_full_orchestrator = _mod.orchestrate_bunker_full_orchestrator
orchestrate_mirror_shadow_dwell = _mod.orchestrate_mirror_shadow_dwell
BunkerOrchestrator = _mod.BunkerOrchestrator
orchestrator = _mod.orchestrator

__all__ = [
    "VETOS_PRIORITY_BETA",
    "append_waitlist_json",
    "orchestrate_beta_waitlist",
    "orchestrate_bunker_full_orchestrator",
    "orchestrate_mirror_shadow_dwell",
    "BunkerOrchestrator",
    "orchestrator",
]
