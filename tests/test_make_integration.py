"""
Tests for the Linear Integration — Protocolo V10 Omega.

Validates that the ZeroSizeEngine computation logic (ported to Python for
server-side verification) and the Make.com integration contract are correct.
"""
from __future__ import annotations

import math
import sys
import os
import unittest

# ---------------------------------------------------------------------------
# Ensure project root is importable (consistent with other test modules).
# ---------------------------------------------------------------------------
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ---------------------------------------------------------------------------
# Minimal Python port of ZeroSizeEngine to verify business logic parity.
# ---------------------------------------------------------------------------
PATENTE = "PCT/EP2025/067317"
PROTOCOL = "ZeroSize-V10-Omega"
_SOVEREIGN_BAND = (0.85, 1.15)


def _calculate_sovereign_fit(scan: dict) -> dict:
    chest = scan.get("chest")
    shoulder = scan.get("shoulder")
    waist = scan.get("waist")
    hip = scan.get("hip")

    has_torso = isinstance(chest, (int, float)) and chest > 0 and \
                isinstance(shoulder, (int, float)) and shoulder > 0
    has_girth = isinstance(chest, (int, float)) and chest > 0 and \
                (isinstance(hip, (int, float)) or isinstance(waist, (int, float)))

    if not has_torso and not has_girth:
        return {
            "torsoRatio": 0,
            "silhouetteIndex": 0,
            "fitDescriptor": "insufficient_data",
            "patente": PATENTE,
            "protocol": PROTOCOL,
        }

    torso_ratio = (shoulder / max(chest, 1e-6)) if has_torso else 0
    reference = hip if (isinstance(hip, (int, float)) and hip > 0) else (waist or 0)
    silhouette_index = (chest / reference) if (has_girth and reference > 0) else 0

    if not has_girth:
        descriptor = "insufficient_data"
    elif _SOVEREIGN_BAND[0] <= silhouette_index <= _SOVEREIGN_BAND[1]:
        descriptor = "sovereign_fit"
    elif silhouette_index < _SOVEREIGN_BAND[0]:
        descriptor = "drape_bias"
    else:
        descriptor = "tension_bias"

    return {
        "torsoRatio": round(torso_ratio, 3),
        "silhouetteIndex": round(silhouette_index, 3),
        "fitDescriptor": descriptor,
        "patente": PATENTE,
        "protocol": PROTOCOL,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestZeroSizeEngine(unittest.TestCase):
    def test_sovereign_fit_balanced_silhouette(self) -> None:
        """chest ≈ hip → silhouetteIndex ≈ 1.0 → sovereign_fit."""
        result = _calculate_sovereign_fit({"chest": 100, "shoulder": 48, "waist": 80, "hip": 100})
        self.assertEqual(result["fitDescriptor"], "sovereign_fit")
        self.assertAlmostEqual(result["silhouetteIndex"], 1.0, places=2)

    def test_drape_bias_narrow_chest(self) -> None:
        """chest < 85% of hip → drape_bias."""
        result = _calculate_sovereign_fit({"chest": 80, "shoulder": 40, "waist": 70, "hip": 100})
        self.assertEqual(result["fitDescriptor"], "drape_bias")
        self.assertLess(result["silhouetteIndex"], _SOVEREIGN_BAND[0])

    def test_tension_bias_wide_chest(self) -> None:
        """chest > 115% of hip → tension_bias."""
        result = _calculate_sovereign_fit({"chest": 120, "shoulder": 50, "waist": 80, "hip": 100})
        self.assertEqual(result["fitDescriptor"], "tension_bias")
        self.assertGreater(result["silhouetteIndex"], _SOVEREIGN_BAND[1])

    def test_insufficient_data_empty_scan(self) -> None:
        result = _calculate_sovereign_fit({})
        self.assertEqual(result["fitDescriptor"], "insufficient_data")
        self.assertEqual(result["torsoRatio"], 0)
        self.assertEqual(result["silhouetteIndex"], 0)

    def test_insufficient_data_only_shoulder(self) -> None:
        """Sin datos de pecho no hay ratio válido."""
        result = _calculate_sovereign_fit({"shoulder": 48})
        self.assertEqual(result["fitDescriptor"], "insufficient_data")

    def test_torso_ratio_computed(self) -> None:
        result = _calculate_sovereign_fit({"chest": 100, "shoulder": 50, "waist": 80})
        self.assertAlmostEqual(result["torsoRatio"], 0.5, places=3)

    def test_waist_used_when_no_hip(self) -> None:
        """Si no hay hip, se usa waist para el índice de silueta."""
        result = _calculate_sovereign_fit({"chest": 90, "shoulder": 45, "waist": 90})
        self.assertAlmostEqual(result["silhouetteIndex"], 1.0, places=3)
        self.assertEqual(result["fitDescriptor"], "sovereign_fit")

    def test_patente_always_present(self) -> None:
        for scan in [{}, {"chest": 100, "shoulder": 48, "waist": 82}]:
            result = _calculate_sovereign_fit(scan)
            self.assertEqual(result["patente"], PATENTE)
            self.assertEqual(result["protocol"], PROTOCOL)


class TestMakeIntegrationContract(unittest.TestCase):
    """Validates the payload shape sent to Make.com."""

    def _build_payload(self, scan: dict) -> dict:
        from datetime import datetime, timezone
        fit = _calculate_sovereign_fit(scan)
        return {
            "patente": PATENTE,
            "fit": fit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "Soberanía Confirmada",
        }

    def test_payload_keys(self) -> None:
        payload = self._build_payload({"chest": 102, "shoulder": 48, "waist": 82})
        self.assertIn("patente", payload)
        self.assertIn("fit", payload)
        self.assertIn("timestamp", payload)
        self.assertIn("status", payload)
        self.assertEqual(payload["patente"], PATENTE)
        self.assertEqual(payload["status"], "Soberanía Confirmada")

    def test_payload_fit_no_raw_measurements(self) -> None:
        """El fit nunca debe exponer medidas corporales brutas (Protocolo Zero-Size)."""
        scan = {"chest": 102, "shoulder": 48, "waist": 82}
        payload = self._build_payload(scan)
        fit = payload["fit"]
        for raw_key in ("chest", "shoulder", "waist", "hip", "height"):
            self.assertNotIn(raw_key, fit, f"Medida bruta '{raw_key}' no debe estar en el fit")

    def test_timestamp_is_iso8601(self) -> None:
        payload = self._build_payload({"chest": 102, "shoulder": 48, "waist": 82})
        from datetime import datetime
        # Should parse without raising.
        ts = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
        self.assertIsNotNone(ts)


if __name__ == "__main__":
    unittest.main()
