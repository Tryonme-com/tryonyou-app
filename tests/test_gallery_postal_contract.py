"""Contrato Python del nodo postal, alineado con src/lib/galleryPostal.js."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GalleryPostalContractTest(unittest.TestCase):
    def test_node_contract(self) -> None:
        completed = subprocess.run(
            ["node", "--test", str(ROOT / "tests" / "test_gallery_postal.mjs")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_shell_scripts_parse(self) -> None:
        scripts = [
            ROOT / "supercommit_max.sh",
            ROOT / "Supercommit_Max",
            ROOT / "SUPERCOMMIT.sh",
            ROOT / "TRYONYOU_SUPERCOMMIT_MAX.sh",
        ]
        for script in scripts:
            completed = subprocess.run(["bash", "-n", str(script)], check=False, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, f"{script.name}: {completed.stderr}")


if __name__ == "__main__":
    unittest.main()
