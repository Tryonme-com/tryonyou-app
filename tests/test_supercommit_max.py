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


class TestWrapperScripts(unittest.TestCase):
    """Verifica que todos los wrappers deleguen en supercommit_max.sh."""

    _WRAPPERS = [
        "SUPERCOMMIT.sh",
        "TRYONYOU_SUPERCOMMIT_MAX.sh",
        "Tryonme_supercommit_max.sh",
        "percommit_max.sh",
    ]

    def _run_wrapper(self, wrapper: str, *args: str) -> subprocess.CompletedProcess:
        script = os.path.join(_ROOT, wrapper)
        return subprocess.run(
            ["bash", script, *args],
            capture_output=True,
            text=True,
            cwd=_ROOT,
        )

    def test_all_wrappers_exist(self) -> None:
        for wrapper in self._WRAPPERS:
            path = os.path.join(_ROOT, wrapper)
            self.assertTrue(os.path.isfile(path), f"Wrapper no encontrado: {wrapper}")

    def test_all_wrappers_valid_bash_syntax(self) -> None:
        for wrapper in self._WRAPPERS:
            path = os.path.join(_ROOT, wrapper)
            result = subprocess.run(["bash", "-n", path], capture_output=True)
            self.assertEqual(
                result.returncode, 0, f"{wrapper} tiene errores de sintaxis bash"
            )

    def test_all_wrappers_delegate_dry_run(self) -> None:
        """Cada wrapper debe producir la misma salida que supercommit_max.sh en dry-run."""
        canonical = subprocess.run(
            ["bash", _SCRIPT, "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            cwd=_ROOT,
        )
        self.assertEqual(canonical.returncode, 0)

        for wrapper in self._WRAPPERS:
            with self.subTest(wrapper=wrapper):
                result = self._run_wrapper(wrapper, "--dry-run", VALID_MSG)
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{wrapper}: returncode={result.returncode}\n{result.stderr}",
                )
                self.assertIn(
                    "Supercommit MAX finalizado",
                    result.stdout,
                    f"{wrapper} no produjo la salida esperada",
                )

    def test_all_wrappers_reject_missing_stamps(self) -> None:
        """Cada wrapper debe rechazar mensajes sin sellos obligatorios."""
        for wrapper in self._WRAPPERS:
            with self.subTest(wrapper=wrapper):
                result = self._run_wrapper(wrapper, "--dry-run", "mensaje-sin-sellos")
                self.assertNotEqual(
                    result.returncode, 0, f"{wrapper} debería rechazar mensajes sin sellos"
                )


class TestCursorRulesCheck(unittest.TestCase):
    """Verifica que supercommit_max.sh comprueba las reglas de Cursor."""

    def test_cursor_rules_verified_message(self) -> None:
        """El script debe indicar que las reglas de Cursor están verificadas."""
        result = subprocess.run(
            ["bash", _SCRIPT, "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            cwd=_ROOT,
        )
        self.assertEqual(result.returncode, 0)
        # El repo tiene .cursor/rules/ — se espera confirmación de verificación
        self.assertIn("Cursor", result.stdout)

    def test_cursor_rules_warning_when_missing(self) -> None:
        """Sin .cursor/rules ni .cursorrules debe emitir un aviso en stderr."""
        import tempfile
        import shutil

        tmpdir = tempfile.mkdtemp()
        try:
            # Copiar solo supercommit_max.sh al dir temporal (sin .cursor/rules)
            shutil.copy(_SCRIPT, tmpdir)
            tmp_script = os.path.join(tmpdir, "supercommit_max.sh")
            result = subprocess.run(
                ["bash", tmp_script, "--dry-run", VALID_MSG],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("AVISO", result.stderr)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestTryonyouSupercommitMax(unittest.TestCase):
    """Verifica el comportamiento de TRYONYOU_SUPERCOMMIT_MAX.sh."""

    _TRYONYOU = os.path.join(_ROOT, "TRYONYOU_SUPERCOMMIT_MAX.sh")

    def _run_tryonyou(self, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
        merged_env = {**os.environ, **(env or {})}
        return subprocess.run(
            ["bash", self._TRYONYOU, *args],
            capture_output=True,
            text=True,
            env=merged_env,
            cwd=_ROOT,
        )

    def test_script_exists(self) -> None:
        self.assertTrue(os.path.isfile(self._TRYONYOU))

    def test_valid_bash_syntax(self) -> None:
        result = subprocess.run(["bash", "-n", self._TRYONYOU], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_fails_without_vite_shop_variant(self) -> None:
        """Sin VITE_SHOP_VARIANT en modo real debe fallar con error descriptivo."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = self._run_tryonyou(VALID_MSG, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VITE_SHOP_VARIANT", result.stderr)

    def test_dryrun_skips_vite_shop_variant_check(self) -> None:
        """En --dry-run debe omitir la verificación de VITE_SHOP_VARIANT."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = self._run_tryonyou("--dry-run", VALID_MSG, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Supercommit MAX finalizado", result.stdout)

    def test_adds_deploy_flag_automatically(self) -> None:
        """Debe añadir --deploy automáticamente (vercel deploy visible en dry-run)."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = self._run_tryonyou("--dry-run", VALID_MSG, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("vercel deploy", result.stdout)

    def test_does_not_duplicate_deploy_flag(self) -> None:
        """Si --deploy ya está presente no debe duplicarlo."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = self._run_tryonyou("--dry-run", "--deploy", VALID_MSG, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("vercel deploy", result.stdout)

    def test_rejects_missing_stamps(self) -> None:
        """Debe rechazar mensajes sin sellos obligatorios."""
        env = {k: v for k, v in os.environ.items() if k != "VITE_SHOP_VARIANT"}
        result = self._run_tryonyou("--dry-run", "mensaje-sin-sellos", env=env)
        self.assertNotEqual(result.returncode, 0)


class TestPercommitFilter(unittest.TestCase):
    """Verifica el filtro de vulgarización de percommit_max.sh."""

    _PERCOMMIT = os.path.join(_ROOT, "percommit_max.sh")

    def _make_git_repo(self) -> str:
        """Crea un repositorio git temporal con los scripts necesarios."""
        import shutil
        import tempfile

        tmpdir = tempfile.mkdtemp()
        subprocess.run(["git", "init"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmpdir, check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmpdir, check=True, capture_output=True,
        )
        shutil.copy(self._PERCOMMIT, tmpdir)
        shutil.copy(_SCRIPT, tmpdir)
        return tmpdir

    def test_script_exists(self) -> None:
        self.assertTrue(os.path.isfile(self._PERCOMMIT))

    def test_valid_bash_syntax(self) -> None:
        result = subprocess.run(["bash", "-n", self._PERCOMMIT], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_dryrun_bypasses_filter(self) -> None:
        """En --dry-run los filtros se omiten."""
        result = subprocess.run(
            ["bash", self._PERCOMMIT, "--dry-run", VALID_MSG],
            capture_output=True,
            text=True,
            cwd=_ROOT,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Supercommit MAX finalizado", result.stdout)

    def test_blocks_size_labels_in_staged_content(self) -> None:
        """Debe bloquear commits con etiquetas de talla S, M o L en el diff staged."""
        import shutil

        tmpdir = self._make_git_repo()
        try:
            test_file = os.path.join(tmpdir, "sizes.txt")
            with open(test_file, "w") as fh:
                fh.write("Available sizes: S M L\n")
            subprocess.run(
                ["git", "add", "sizes.txt"],
                cwd=tmpdir, check=True, capture_output=True,
            )
            result = subprocess.run(
                ["bash", "percommit_max.sh", VALID_MSG],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOQUEADO", result.stderr)
            self.assertIn("talla", result.stderr)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_blocks_shopify_admin_token_shpat(self) -> None:
        """Debe bloquear commits que expongan un token shpat_ de Shopify."""
        import shutil

        tmpdir = self._make_git_repo()
        try:
            test_file = os.path.join(tmpdir, "config.py")
            with open(test_file, "w") as fh:
                fh.write("TOKEN = 'shpat_abc123XYZ'\n")
            subprocess.run(
                ["git", "add", "config.py"],
                cwd=tmpdir, check=True, capture_output=True,
            )
            result = subprocess.run(
                ["bash", "percommit_max.sh", VALID_MSG],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOQUEADO", result.stderr)
            self.assertIn("Shopify", result.stderr)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_blocks_shopify_admin_access_token_assignment(self) -> None:
        """Debe bloquear commits que expongan SHOPIFY_ADMIN_ACCESS_TOKEN con valor."""
        import shutil

        tmpdir = self._make_git_repo()
        try:
            test_file = os.path.join(tmpdir, ".env")
            with open(test_file, "w") as fh:
                fh.write("SHOPIFY_ADMIN_ACCESS_TOKEN=shpat_secrettoken123\n")
            subprocess.run(
                ["git", "add", ".env"],
                cwd=tmpdir, check=True, capture_output=True,
            )
            result = subprocess.run(
                ["bash", "percommit_max.sh", VALID_MSG],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOQUEADO", result.stderr)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_allows_empty_shopify_token_assignment(self) -> None:
        """SHOPIFY_ADMIN_ACCESS_TOKEN= sin valor (como en .env.example) no debe bloquearse."""
        import shutil

        tmpdir = self._make_git_repo()
        try:
            test_file = os.path.join(tmpdir, ".env.example")
            with open(test_file, "w") as fh:
                fh.write("SHOPIFY_ADMIN_ACCESS_TOKEN=\n")
            subprocess.run(
                ["git", "add", ".env.example"],
                cwd=tmpdir, check=True, capture_output=True,
            )
            result = subprocess.run(
                ["bash", "percommit_max.sh", VALID_MSG],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
            # Should not be blocked by the Shopify token filter
            # (may still fail at git commit/push, but not due to the token filter)
            self.assertNotIn("BLOQUEADO", result.stderr)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
