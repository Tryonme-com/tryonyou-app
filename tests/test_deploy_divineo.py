"""Cobertura de salida para deploy_divineo.py (Protocolo OMEGA V10)."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from deploy_divineo import PATENT, SOVEREIGN_PROTOCOL, deploy_divineo


class TestDeployDivineo(unittest.TestCase):
    def test_deploy_divineo_prints_full_final_block(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            deploy_divineo(nodes=("Core", "Security"), delay_seconds=0.0)

        output = buffer.getvalue()
        self.assertIn("INICIANDO DESPLIEGUE OMEGA", output)
        self.assertIn("Sincronizando Nodo CORE", output)
        self.assertIn("Sincronizando Nodo SECURITY", output)
        self.assertIn("PALOMA LAFAYETTE: SYNC COMPLETE", output)
        self.assertIn("GEMELO DIGITAL: 99.7% ACCURACY", output)
        self.assertIn("STATUS: VIVOS", output)
        self.assertIn(PATENT, output)
        self.assertIn(SOVEREIGN_PROTOCOL, output)


if __name__ == "__main__":
    unittest.main()
