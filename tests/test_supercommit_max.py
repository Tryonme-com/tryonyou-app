"""Tests para supercommit_max.sh, TRYONYOU_SUPERCOMMIT_MAX.sh y percommit_max.sh."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

# Ruta al script desde la raíz del proyecto
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPT = os.path.join(_ROOT, "supercommit_max.sh")
_TRYONYOU_SCRIPT = os.path.join(_ROOT, "TRYONYOU_SUPERCOMMIT_MAX.sh")
_PERCOMMIT_SCRIPT = os.path.join(_ROOT, "percommit_max.sh")

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
        # Un mensaje sin sellos debe ser rechazado explícitamente
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


class TestTryonyouSupercommitMax(unittest.TestCase):
    """Verifica TRYONYOU_SUPERCOMMIT_MAX.sh: sintaxis, env guard y cache clean."""

    def test_script_exists(self) -> None:
        self.assertTrue(os.path.isfile(_TRYONYOU_SCRIPT), f"Script no encontrado: {_TRYONYOU_SCRIPT}")

    def test_script_valid_bash_syntax(self) -> None:
        result = subprocess.run(["bash", "-n", _TRYONYOU_SCRIPT], capture_output=True)
        self.assertEqual(result.returncode, 0, "TRYONYOU_SUPERCOMMIT_MAX.sh tiene errores de sintaxis bash")

    def test_requires_vite_shop_variant(self) -> None:
        """Sin VITE_SHOP_VARIANT el script debe abortar con error."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = subprocess.run(
            ["bash", _TRYONYOU_SCRIPT, "--skip-cache-clean", "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            env=env,
            cwd=_ROOT,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VITE_SHOP_VARIANT", result.stderr)

    def test_skip_env_check_bypasses_vite_guard(self) -> None:
        """--skip-env-check debe omitir la verificación de VITE_SHOP_VARIANT."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = subprocess.run(
            ["bash", _TRYONYOU_SCRIPT, "--skip-env-check", "--skip-cache-clean", "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            env=env,
            cwd=_ROOT,
        )
        self.assertEqual(result.returncode, 0)

    def test_with_vite_shop_variant_reports_it(self) -> None:
        """Con VITE_SHOP_VARIANT definida el script la reporta."""
        env = {**os.environ, "VITE_SHOP_VARIANT": "test-variant-42"}
        result = subprocess.run(
            ["bash", _TRYONYOU_SCRIPT, "--skip-cache-clean", "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            env=env,
            cwd=_ROOT,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("test-variant-42", result.stdout)

    def test_delegates_to_supercommit_max(self) -> None:
        """Tras los checks propios el script debe terminar con el sello de supercommit_max."""
        env = {**os.environ, "VITE_SHOP_VARIANT": "v1"}
        result = subprocess.run(
            ["bash", _TRYONYOU_SCRIPT, "--skip-cache-clean", "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            env=env,
            cwd=_ROOT,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Supercommit MAX finalizado", result.stdout)


class TestPercommitMax(unittest.TestCase):
    """Verifica percommit_max.sh: filtro de tallas y de Shopify Admin Token."""

    def _run_percommit(self, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
        merged_env = {**os.environ, **(env or {})}
        return subprocess.run(
            ["bash", _PERCOMMIT_SCRIPT, *args],
            capture_output=True,
            text=True,
            env=merged_env,
            cwd=_ROOT,
        )

    def test_script_exists(self) -> None:
        self.assertTrue(os.path.isfile(_PERCOMMIT_SCRIPT), f"Script no encontrado: {_PERCOMMIT_SCRIPT}")

    def test_script_valid_bash_syntax(self) -> None:
        result = subprocess.run(["bash", "-n", _PERCOMMIT_SCRIPT], capture_output=True)
        self.assertEqual(result.returncode, 0, "percommit_max.sh tiene errores de sintaxis bash")

    def test_skip_security_check_delegates(self) -> None:
        """--skip-security-check debe omitir los filtros y delegar en supercommit_max."""
        result = self._run_percommit("--skip-security-check", "--dry-run", VALID_MSG)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Supercommit MAX finalizado", result.stdout)

    def test_shopify_token_in_staged_is_blocked(self) -> None:
        """Un token shpat_… en el diff staged debe ser rechazado."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init", tmpdir], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "config", "user.email", "test@test.com"], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "config", "user.name", "Test"], capture_output=True)
            # Crea un commit inicial para que el diff funcione
            init_file = os.path.join(tmpdir, "init.txt")
            with open(init_file, "w") as f:
                f.write("init\n")
            subprocess.run(["git", "-C", tmpdir, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", tmpdir, "commit", "-m", "init"], capture_output=True)
            # Ahora añade un archivo con un token de Shopify
            secret_file = os.path.join(tmpdir, "secret.txt")
            with open(secret_file, "w") as f:
                f.write("SHOPIFY_TOKEN=shpat_abcdefghij1234567890\n")
            subprocess.run(["git", "-C", tmpdir, "add", "."], capture_output=True)
            result = subprocess.run(
                ["bash", _PERCOMMIT_SCRIPT, "--dry-run", VALID_MSG],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Shopify", result.stderr)


if __name__ == "__main__":
    unittest.main()
