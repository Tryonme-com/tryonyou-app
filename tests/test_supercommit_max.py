"""Tests para supercommit_max.sh — Protocolo de sellos TryOnYou."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPT = os.path.join(_ROOT, "supercommit_max.sh")

# Mensaje válido con todos los sellos requeridos.
_VALID_MSG = (
    "Prueba @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

# Sellos que deben aparecer en el mensaje de commit.
_REQUIRED_STAMPS = [
    "@CertezaAbsoluta",
    "@lo+erestu",
    "PCT/EP2025/067317",
    "Bajo Protocolo de Soberanía V10",
    "Founder: Rubén",
]


def _init_git_repo(path: str) -> None:
    """Initialise a minimal bare git repo so commits work without a remote."""
    subprocess.check_call(["git", "init", "-b", "main", path],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(
        ["git", "config", "user.email", "test@tryonyou.app"], cwd=path,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        ["git", "config", "user.name", "TryOnYou Test"], cwd=path,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # Commit inicial vacío para que la rama exista.
    subprocess.check_call(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=path,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _run_script(cwd: str, args: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = ["bash", _SCRIPT] + (args or [])
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class TestScriptExists(unittest.TestCase):
    def test_script_file_exists(self) -> None:
        self.assertTrue(os.path.isfile(_SCRIPT), f"Falta {_SCRIPT}")

    def test_script_is_executable(self) -> None:
        mode = os.stat(_SCRIPT).st_mode
        self.assertTrue(mode & stat.S_IXUSR, "supercommit_max.sh no es ejecutable")


class TestRequiredStamps(unittest.TestCase):
    """El script rechaza mensajes sin los sellos obligatorios."""

    def _assert_rejected(self, msg: str, missing_stamp: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _init_git_repo(tmp)
            result = _run_script(tmp, [msg])
        self.assertNotEqual(result.returncode, 0,
                            f"Debería rechazar mensaje sin {missing_stamp!r}")
        self.assertIn("Falta", result.stderr,
                      f"Mensaje de error esperado en stderr al faltar {missing_stamp!r}")

    def test_rejects_message_missing_certeza_absoluta(self) -> None:
        msg = _VALID_MSG.replace("@CertezaAbsoluta", "")
        self._assert_rejected(msg, "@CertezaAbsoluta")

    def test_rejects_message_missing_lo_erestu(self) -> None:
        msg = _VALID_MSG.replace("@lo+erestu", "")
        self._assert_rejected(msg, "@lo+erestu")

    def test_rejects_message_missing_patente(self) -> None:
        msg = _VALID_MSG.replace("PCT/EP2025/067317", "")
        self._assert_rejected(msg, "PCT/EP2025/067317")

    def test_rejects_message_missing_protocolo(self) -> None:
        msg = _VALID_MSG.replace("Bajo Protocolo de Soberanía V10", "")
        self._assert_rejected(msg, "Bajo Protocolo de Soberanía V10")

    def test_rejects_message_missing_founder(self) -> None:
        msg = _VALID_MSG.replace("Founder: Rubén", "")
        self._assert_rejected(msg, "Founder: Rubén")

    def test_rejects_empty_message(self) -> None:
        # Un mensaje vacío carece de todos los sellos.
        with tempfile.TemporaryDirectory() as tmp:
            _init_git_repo(tmp)
            result = _run_script(tmp, [""])
        self.assertNotEqual(result.returncode, 0)


def _setup_isolated_repo() -> "tempfile.TemporaryDirectory[str]":
    """Create a temp dir with an initialised git repo AND a copy of the script
    already committed so it doesn't appear as a pending change.

    The script contains ``cd "$ROOT"`` (ROOT = dir of the script itself), so
    placing the script inside the temp git repo makes both coincide.

    Use as a context manager: ``with _setup_isolated_repo() as tmp:``
    where *tmp* is the path string yielded by TemporaryDirectory.__enter__.
    """
    tmp_obj = tempfile.TemporaryDirectory()
    tmp = tmp_obj.name
    subprocess.check_call(["git", "init", "-b", "main", tmp],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for cmd in (
        ["git", "config", "user.email", "test@tryonyou.app"],
        ["git", "config", "user.name", "TryOnYou Test"],
    ):
        subprocess.check_call(cmd, cwd=tmp,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Copy the script and commit it so it is already tracked.
    shutil.copy2(_SCRIPT, os.path.join(tmp, "supercommit_max.sh"))
    os.chmod(os.path.join(tmp, "supercommit_max.sh"), 0o755)
    subprocess.check_call(
        ["git", "add", "supercommit_max.sh"], cwd=tmp,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        ["git", "commit", "-m", "add supercommit_max.sh"],
        cwd=tmp,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return tmp_obj


class TestValidMessage(unittest.TestCase):
    """Con el mensaje correcto el script llega hasta la fase de push."""

    def test_accepts_valid_message_no_remote(self) -> None:
        """Script acepta mensaje válido; sin remote sale limpio (sin push)."""
        with _setup_isolated_repo() as tmp:
            script = os.path.join(tmp, "supercommit_max.sh")
            # Crear un fichero para tener algo que commitear.
            open(os.path.join(tmp, "dummy.txt"), "w").close()
            result = subprocess.run(
                ["bash", script, _VALID_MSG],
                cwd=tmp, capture_output=True, text=True,
            )
        # Sin upstream configurado, el script no empuja y termina con éxito.
        self.assertEqual(result.returncode, 0,
                         f"stdout={result.stdout}\nstderr={result.stderr}")

    def test_no_changes_exits_cleanly(self) -> None:
        """Sin cambios pendientes el script sale con código 0 (nada que hacer)."""
        with _setup_isolated_repo() as tmp:
            script = os.path.join(tmp, "supercommit_max.sh")
            result = subprocess.run(
                ["bash", script, _VALID_MSG],
                cwd=tmp, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0,
                         f"stdout={result.stdout}\nstderr={result.stderr}")

    def test_commit_uses_provided_message(self) -> None:
        """El commit creado debe contener el mensaje proporcionado."""
        with _setup_isolated_repo() as tmp:
            script = os.path.join(tmp, "supercommit_max.sh")
            open(os.path.join(tmp, "file.txt"), "w").close()
            subprocess.run(
                ["bash", script, _VALID_MSG],
                cwd=tmp, capture_output=True, text=True,
            )
            log = subprocess.check_output(
                ["git", "log", "--format=%s", "-1"], cwd=tmp, text=True
            ).strip()
        # El asunto del commit debe incluir el texto exacto dado.
        self.assertIn("@CertezaAbsoluta", log)
        self.assertIn("PCT/EP2025/067317", log)


class TestDefaultMessage(unittest.TestCase):
    """Sin argumento, el script usa el mensaje por defecto que ya contiene los sellos."""

    def test_default_message_contains_all_stamps(self) -> None:
        """El mensaje por defecto embebido en el script tiene todos los sellos."""
        with open(_SCRIPT, encoding="utf-8") as fh:
            source = fh.read()
        for stamp in _REQUIRED_STAMPS:
            self.assertIn(stamp, source,
                          f"El mensaje por defecto del script no contiene {stamp!r}")


if __name__ == "__main__":
    unittest.main()
