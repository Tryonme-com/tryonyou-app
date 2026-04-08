"""Tests para hulk_git_operations — hulk_clean_everything() y push_to_git()."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import hulk_git_operations


def _reset_cleaned() -> None:
    """Reinicia el flag interno de sesión entre tests."""
    hulk_git_operations._cleaned = False


class TestHulkCleanEverything(unittest.TestCase):
    def setUp(self) -> None:
        _reset_cleaned()

    def test_returns_string(self) -> None:
        """hulk_clean_everything() debe devolver una cadena de texto."""
        with patch("hulk_git_operations.BunkerCleaner") as MockCleaner:
            instance = MockCleaner.return_value
            instance.ejecutar_limpieza.return_value = "✨ Búnker limpio."
            result = hulk_git_operations.hulk_clean_everything()
        self.assertIsInstance(result, str)

    def test_sets_cleaned_flag(self) -> None:
        """hulk_clean_everything() debe activar el flag interno _cleaned."""
        self.assertFalse(hulk_git_operations._cleaned)
        with patch("hulk_git_operations.BunkerCleaner") as MockCleaner:
            MockCleaner.return_value.ejecutar_limpieza.return_value = "ok"
            hulk_git_operations.hulk_clean_everything()
        self.assertTrue(hulk_git_operations._cleaned)

    def test_delegates_to_bunker_cleaner(self) -> None:
        """hulk_clean_everything() debe delegar en BunkerCleaner.ejecutar_limpieza."""
        with patch("hulk_git_operations.BunkerCleaner") as MockCleaner:
            instance = MockCleaner.return_value
            instance.ejecutar_limpieza.return_value = "limpio"
            result = hulk_git_operations.hulk_clean_everything()
        instance.ejecutar_limpieza.assert_called_once()
        self.assertEqual(result, "limpio")


class TestPushToGit(unittest.TestCase):
    def setUp(self) -> None:
        _reset_cleaned()

    # ------------------------------------------------------------------
    # Guardia: limpieza previa requerida
    # ------------------------------------------------------------------

    def test_blocks_if_not_cleaned(self) -> None:
        """push_to_git() debe rechazar el push si hulk_clean_everything() no se ejecutó."""
        result = hulk_git_operations.push_to_git()
        self.assertIn("hulk_clean_everything()", result)
        self.assertIn("⛔", result)

    # ------------------------------------------------------------------
    # Guardia: E50_GIT_PUSH=1 requerido
    # ------------------------------------------------------------------

    def test_blocks_without_e50_git_push(self) -> None:
        """push_to_git() debe detenerse si E50_GIT_PUSH no está definido."""
        hulk_git_operations._cleaned = True
        env_without = {k: v for k, v in os.environ.items() if k != "E50_GIT_PUSH"}
        with patch.dict(os.environ, env_without, clear=True):
            result = hulk_git_operations.push_to_git()
        self.assertIn("E50_GIT_PUSH=1", result)

    # ------------------------------------------------------------------
    # Guardia: repositorio Git no encontrado
    # ------------------------------------------------------------------

    def test_blocks_if_no_git_dir(self) -> None:
        """push_to_git() debe detenerse si no hay .git en la raíz."""
        import tempfile

        hulk_git_operations._cleaned = True
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {"E50_GIT_PUSH": "1", "E50_PROJECT_ROOT": tmp_dir}):
                result = hulk_git_operations.push_to_git()
        self.assertIn("No se encontró repositorio Git", result)

    # ------------------------------------------------------------------
    # Guardia: árbol de trabajo no limpio
    # ------------------------------------------------------------------

    def test_blocks_if_dirty_working_tree(self) -> None:
        """push_to_git() debe rechazar el push si hay cambios sin confirmar."""
        hulk_git_operations._cleaned = True

        dirty_status = MagicMock()
        dirty_status.returncode = 0
        dirty_status.stdout = " M some_file.py\n"
        dirty_status.stderr = ""

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}), \
             patch("hulk_git_operations._root") as mock_root, \
             patch("hulk_git_operations._run", return_value=dirty_status):
            mock_root.return_value = MagicMock(**{"__truediv__": lambda s, x: MagicMock(is_dir=lambda: True)})
            result = hulk_git_operations.push_to_git()

        self.assertIn("⚠️", result)
        self.assertIn("no está limpio", result)

    # ------------------------------------------------------------------
    # Flujo exitoso
    # ------------------------------------------------------------------

    def test_push_succeeds_when_clean(self) -> None:
        """push_to_git() debe completar el push cuando el árbol es limpio."""
        hulk_git_operations._cleaned = True

        def fake_run(argv: list[str], *, cwd) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            if "status" in argv:
                result.stdout = ""
                result.stderr = ""
            elif "rev-parse" in argv:
                result.stdout = "main"
                result.stderr = ""
            else:
                result.stdout = ""
                result.stderr = ""
            return result

        git_dir_mock = MagicMock()
        git_dir_mock.is_dir.return_value = True

        def fake_truediv(self_val, key: str) -> MagicMock:
            return git_dir_mock

        root_mock = MagicMock()
        root_mock.__truediv__ = fake_truediv

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1", "E50_GIT_REMOTE": "origin", "E50_GIT_BRANCH": "main"}), \
             patch("hulk_git_operations._root", return_value=root_mock), \
             patch("hulk_git_operations._run", side_effect=fake_run):
            result = hulk_git_operations.push_to_git()

        self.assertIn("✅", result)
        self.assertIn("origin/main", result)

    def test_push_respects_force_flag(self) -> None:
        """push_to_git() debe añadir --force cuando E50_FORCE_PUSH=1."""
        hulk_git_operations._cleaned = True
        calls: list[list[str]] = []

        def fake_run(argv: list[str], *, cwd) -> MagicMock:
            calls.append(argv)
            result = MagicMock()
            result.returncode = 0
            result.stdout = "" if "status" in argv or "push" in argv else "main"
            result.stderr = ""
            return result

        git_dir_mock = MagicMock()
        git_dir_mock.is_dir.return_value = True
        root_mock = MagicMock()
        root_mock.__truediv__ = lambda s, k: git_dir_mock

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1", "E50_FORCE_PUSH": "1",
                                      "E50_GIT_BRANCH": "main"}), \
             patch("hulk_git_operations._root", return_value=root_mock), \
             patch("hulk_git_operations._run", side_effect=fake_run):
            hulk_git_operations.push_to_git()

        push_call = next((c for c in calls if "push" in c), None)
        self.assertIsNotNone(push_call)
        self.assertIn("--force", push_call)

    def test_push_fails_on_git_error(self) -> None:
        """push_to_git() debe retornar mensaje de error cuando git push falla."""
        hulk_git_operations._cleaned = True

        def fake_run(argv: list[str], *, cwd) -> MagicMock:
            result = MagicMock()
            if "status" in argv:
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
            elif "rev-parse" in argv:
                result.returncode = 0
                result.stdout = "main"
                result.stderr = ""
            else:
                result.returncode = 1
                result.stdout = ""
                result.stderr = "error: unable to connect to remote"
            return result

        git_dir_mock = MagicMock()
        git_dir_mock.is_dir.return_value = True
        root_mock = MagicMock()
        root_mock.__truediv__ = lambda s, k: git_dir_mock

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1", "E50_GIT_BRANCH": "main"}), \
             patch("hulk_git_operations._root", return_value=root_mock), \
             patch("hulk_git_operations._run", side_effect=fake_run):
            result = hulk_git_operations.push_to_git()

        self.assertIn("❌", result)
        self.assertIn("git push falló", result)


if __name__ == "__main__":
    unittest.main()
