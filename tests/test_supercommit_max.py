"""Tests para supercommit_max.sh — valida sellos, opciones y flujo dry-run."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

# Ruta al script desde la raíz del proyecto
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPT = os.path.join(_ROOT, "supercommit_max.sh")

VALID_MSG = "Deploy V10 @CertezaAbsoluta @lo+erestu PCT/EP2025/067317"


def _run(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Ejecuta supercommit_max.sh con los argumentos indicados."""
    merged_env = {**os.environ, **(env or {})}
    return subprocess.run(
        ["bash", _SCRIPT, *args],
        capture_output=True,
        text=True,
        env=merged_env,
        cwd=_ROOT,
    )


class TestScriptExists(unittest.TestCase):
    def test_script_exists(self) -> None:
        self.assertTrue(os.path.isfile(_SCRIPT), f"Script no encontrado: {_SCRIPT}")

    def test_script_is_executable_bash(self) -> None:
        result = subprocess.run(["bash", "-n", _SCRIPT], capture_output=True)
        self.assertEqual(result.returncode, 0, "El script tiene errores de sintaxis bash")


class TestHelp(unittest.TestCase):
    def test_help_short(self) -> None:
        result = _run("-h")
        self.assertEqual(result.returncode, 0)
        self.assertIn("@CertezaAbsoluta", result.stdout)

    def test_help_long(self) -> None:
        result = _run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--build", result.stdout)
        self.assertIn("--deploy", result.stdout)
        self.assertIn("--force", result.stdout)


class TestStampValidation(unittest.TestCase):
    """Verifica que el script rechaza mensajes sin los tres sellos obligatorios."""

    def test_rejects_missing_certeza(self) -> None:
        result = _run("--dry-run", "Mensaje @lo+erestu PCT/EP2025/067317")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CertezaAbsoluta", result.stderr)

    def test_rejects_missing_loerestu(self) -> None:
        result = _run("--dry-run", "Mensaje @CertezaAbsoluta PCT/EP2025/067317")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lo+erestu", result.stderr)

    def test_rejects_missing_patent(self) -> None:
        result = _run("--dry-run", "Mensaje @CertezaAbsoluta @lo+erestu")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PCT/EP2025/067317", result.stderr)

    def test_rejects_empty_message(self) -> None:
        # Un mensaje sin sellos explícito debe ser rechazado
        result = _run("--dry-run", "sin-sellos-aqui")
        self.assertNotEqual(result.returncode, 0)

    def test_accepts_valid_message(self) -> None:
        result = _run("--dry-run", VALID_MSG)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Supercommit MAX finalizado", result.stdout)

    def test_default_message_has_all_stamps(self) -> None:
        """Sin mensaje explícito el mensaje por defecto debe pasar la validación."""
        result = _run("--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Supercommit MAX finalizado", result.stdout)


class TestDryRun(unittest.TestCase):
    """Verifica que --dry-run muestra los comandos sin ejecutarlos."""

    def test_dryrun_shows_git_add(self) -> None:
        result = _run("--dry-run", VALID_MSG)
        self.assertIn("[DRY-RUN]", result.stdout)
        self.assertIn("git add -A", result.stdout)

    def test_dryrun_shows_git_commit(self) -> None:
        result = _run("--dry-run", VALID_MSG)
        self.assertIn("git commit -m", result.stdout)

    def test_dryrun_shows_git_push(self) -> None:
        result = _run("--dry-run", VALID_MSG)
        self.assertIn("git push", result.stdout)

    def test_dryrun_build_shows_npm(self) -> None:
        result = _run("--dry-run", "--build", VALID_MSG)
        self.assertIn("npm install", result.stdout)
        self.assertIn("npm run build", result.stdout)

    def test_dryrun_deploy_shows_vercel(self) -> None:
        result = _run("--dry-run", "--deploy", VALID_MSG)
        self.assertEqual(result.returncode, 0)
        self.assertIn("vercel deploy", result.stdout)

    def test_dryrun_force_shows_force_with_lease(self) -> None:
        result = _run("--dry-run", "--force", VALID_MSG)
        self.assertIn("--force-with-lease", result.stdout)


class TestDeployRequiresToken(unittest.TestCase):
    """Verifica que --deploy sin VERCEL_TOKEN falla fuera de dry-run."""

    def test_deploy_without_token_fails(self) -> None:
        # Eliminamos VERCEL_TOKEN si existiera en el entorno
        env = {k: v for k, v in os.environ.items() if k != "VERCEL_TOKEN"}
        result = subprocess.run(
            ["bash", _SCRIPT, "--deploy", VALID_MSG],
            capture_output=True,
            text=True,
            env=env,
            cwd=_ROOT,
        )
        # El script debe salir con error cuando no hay VERCEL_TOKEN
        # (a menos que la ejecución de git push falle antes, lo cual también da error)
        self.assertNotEqual(result.returncode, 0)

    def test_deploy_dryrun_without_token_succeeds(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "VERCEL_TOKEN"}
        result = subprocess.run(
            ["bash", _SCRIPT, "--dry-run", "--deploy", VALID_MSG],
            capture_output=True,
            text=True,
            env=env,
            cwd=_ROOT,
        )
        self.assertEqual(result.returncode, 0)


class TestUnknownOption(unittest.TestCase):
    def test_unknown_option_exits_nonzero(self) -> None:
        result = _run("--unknown-flag", VALID_MSG)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Opción desconocida", result.stderr)


if __name__ == "__main__":
    unittest.main()
