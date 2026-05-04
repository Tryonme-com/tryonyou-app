from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from prepare_email_package import EMAIL_TEMPLATE, default_export_dir, prepare_package


class TestPrepareEmailPackage(unittest.TestCase):
    def test_prepare_package_writes_email_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = prepare_package(export_dir=tmp, assets=())

            template_path = destination / "EMAIL_TEMPLATE.txt"
            self.assertTrue(template_path.exists())
            self.assertEqual(template_path.read_text(encoding="utf-8"), EMAIL_TEMPLATE)

    def test_prepare_package_copies_existing_assets_only(self) -> None:
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as output:
            Path(source, "validation.pdf").write_text("ok", encoding="utf-8")

            destination = prepare_package(
                export_dir=output,
                source_dir=source,
                assets=("validation.pdf", "missing.pdf"),
            )

            self.assertTrue((destination / "validation.pdf").exists())
            self.assertFalse((destination / "missing.pdf").exists())

    def test_default_export_dir_falls_back_to_temp_when_desktop_missing(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            with patch("pathlib.Path.home", return_value=Path(home)):
                self.assertEqual(
                    default_export_dir(),
                    Path(tempfile.gettempdir()) / "TRYONYOU_COMMERCIAL_PACKAGE",
                )


if __name__ == "__main__":
    unittest.main()
