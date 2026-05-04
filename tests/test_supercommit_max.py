"""Tests para supercommit_max.sh v10.17 VIVOS — validación de sellos, modos y lógica de push."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPT = os.path.join(_ROOT, "supercommit_max.sh")

VALID_MSG = (
    "Título @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_script(*args: str, cwd: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run supercommit_max.sh with the given arguments and return the result."""
    cmd = ["bash", _SCRIPT] + list(args)
    base_env = os.environ.copy()
    if env:
        base_env.update(env)
    return subprocess.run(
        cmd,
        cwd=cwd or _ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        env=base_env,
    )


def _init_git_repo(path: str) -> None:
    """Initialise a minimal git repo with one initial commit."""
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@tryonyou.app"],
        cwd=path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "TryOnYou Test"],
        cwd=path, check=True, capture_output=True,
    )
    readme = os.path.join(path, "README.md")
    with open(readme, "w") as fh:
        fh.write("# test\n")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=path, check=True, capture_output=True,
    )


# ---------------------------------------------------------------------------
# Existence / metadata
# ---------------------------------------------------------------------------


class TestScriptExists(unittest.TestCase):
    def test_script_file_exists(self) -> None:
        self.assertTrue(os.path.isfile(_SCRIPT), f"Script not found: {_SCRIPT}")

    def test_script_is_readable(self) -> None:
        self.assertTrue(os.access(_SCRIPT, os.R_OK))

    def test_script_starts_with_shebang(self) -> None:
        with open(_SCRIPT) as fh:
            first_line = fh.readline()
        self.assertTrue(first_line.startswith("#!"), "Script should start with a shebang (#!)")

    def test_script_uses_bash(self) -> None:
        with open(_SCRIPT) as fh:
            first_line = fh.readline()
        self.assertIn("bash", first_line)


# ---------------------------------------------------------------------------
# Stamp validation — v10.17 auto-appends stamps to custom messages
# ---------------------------------------------------------------------------


class TestStampValidation(unittest.TestCase):
    """v10.17 auto-appends stamps when --msg lacks them; explicit stamps are preserved."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        _init_git_repo(self.tmpdir)
        self.script_copy = os.path.join(self.tmpdir, "supercommit_max.sh")
        shutil.copy2(_SCRIPT, self.script_copy)
        subprocess.run(["git", "add", "supercommit_max.sh"], cwd=self.tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "add script copy"],
            cwd=self.tmpdir, check=True, capture_output=True,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", self.script_copy] + list(args),
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "HOME": self.tmpdir},
        )

    def test_explicit_stamps_preserved(self) -> None:
        result = self._run("--fast", "--msg", VALID_MSG)
        self.assertNotIn("Falta", result.stderr)

    def test_auto_appended_stamps_pass_validation(self) -> None:
        result = self._run("--fast", "--msg", "Custom sin sellos")
        self.assertNotIn("Falta", result.stderr)

    def test_default_msg_does_not_fail_on_stamps(self) -> None:
        result = self._run("--fast")
        self.assertNotIn("Falta", result.stderr)

    def test_default_msg_not_exit_1_due_to_stamps(self) -> None:
        result = self._run("--fast")
        if result.returncode == 1:
            self.fail(f"Default message failed stamp validation. stderr={result.stderr!r}")


# ---------------------------------------------------------------------------
# Mode flags
# ---------------------------------------------------------------------------


class TestModeFlags(unittest.TestCase):
    """Verify that --fast, --deploy, --msg are accepted."""

    def test_fast_mode_skips_build(self) -> None:
        result = _run_script("--fast")
        self.assertNotIn("Vite production build", result.stdout)
        self.assertNotIn("Python tests", result.stdout)

    def test_deploy_mode_without_token_fails(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "VERCEL_TOKEN"}
        env["VERCEL_TOKEN"] = ""
        result = _run_script("--fast", "--deploy", env=env)
        self.assertNotEqual(result.returncode, 0)

    def test_msg_flag_sets_custom_message(self) -> None:
        result = _run_script("--fast", "--msg", "Hola mundo custom")
        self.assertNotIn("Falta", result.stderr)


# ---------------------------------------------------------------------------
# Commit logic in isolated git repo (--fast mode)
# ---------------------------------------------------------------------------


class TestCommitLogic(unittest.TestCase):
    """Run the script in --fast mode in a temporary, isolated git repository."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        _init_git_repo(self.tmpdir)
        self.script_copy = os.path.join(self.tmpdir, "supercommit_max.sh")
        shutil.copy2(_SCRIPT, self.script_copy)
        subprocess.run(["git", "add", "supercommit_max.sh"], cwd=self.tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "add script copy"],
            cwd=self.tmpdir, check=True, capture_output=True,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        cmd = ["bash", self.script_copy] + list(args)
        return subprocess.run(
            cmd,
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "HOME": self.tmpdir},
        )

    def test_nothing_to_commit_no_push_without_upstream(self) -> None:
        result = self._run("--fast", "--msg", VALID_MSG)
        combined = result.stdout + result.stderr
        self.assertNotIn("Falta", result.stderr)
        self.assertTrue(
            "upstream" in combined.lower() or "nada nuevo" in combined.lower()
            or "@{u}" in combined,
        )

    def test_new_file_is_committed(self) -> None:
        new_file = os.path.join(self.tmpdir, "nuevo.txt")
        with open(new_file, "w") as fh:
            fh.write("hola\n")
        result = self._run("--fast", "--msg", VALID_MSG)
        self.assertNotIn("Falta", result.stderr)
        log = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=self.tmpdir, capture_output=True, text=True,
        )
        self.assertIn("Título", log.stdout)

    def test_commit_message_contains_patente(self) -> None:
        new_file = os.path.join(self.tmpdir, "patente_test.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        self._run("--fast", "--msg", VALID_MSG)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir, capture_output=True, text=True,
        )
        self.assertIn("PCT/EP2025/067317", log.stdout)

    def test_commit_message_contains_certeza_absoluta(self) -> None:
        new_file = os.path.join(self.tmpdir, "certeza.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        self._run("--fast", "--msg", VALID_MSG)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir, capture_output=True, text=True,
        )
        self.assertIn("@CertezaAbsoluta", log.stdout)

    def test_commit_message_contains_protocolo_soberania(self) -> None:
        new_file = os.path.join(self.tmpdir, "soberania.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        self._run("--fast", "--msg", VALID_MSG)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir, capture_output=True, text=True,
        )
        self.assertIn("Bajo Protocolo de Soberanía V10", log.stdout)

    def test_auto_stamp_append_on_custom_msg(self) -> None:
        """Custom message without stamps gets stamps auto-appended."""
        new_file = os.path.join(self.tmpdir, "auto_stamp.txt")
        with open(new_file, "w") as fh:
            fh.write("test\n")
        self._run("--fast", "--msg", "Mi commit custom")
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir, capture_output=True, text=True,
        )
        self.assertIn("PCT/EP2025/067317", log.stdout)
        self.assertIn("@CertezaAbsoluta", log.stdout)
        self.assertIn("Founder: Rubén", log.stdout)

    def test_no_changes_outputs_nada_nuevo(self) -> None:
        result = self._run("--fast", "--msg", VALID_MSG)
        combined = result.stdout.lower()
        self.assertTrue("nada nuevo" in combined or "sin commit" in combined)

    def test_default_message_in_isolated_repo(self) -> None:
        new_file = os.path.join(self.tmpdir, "default_msg.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        result = self._run("--fast")
        self.assertNotIn("Falta", result.stderr)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir, capture_output=True, text=True,
        )
        self.assertIn("OMEGA_DEPLOY", log.stdout)

    def test_sensitive_env_files_are_not_staged(self) -> None:
        with open(os.path.join(self.tmpdir, ".env"), "w") as fh:
            fh.write("SECRET=must_not_commit\n")
        with open(os.path.join(self.tmpdir, ".env.production"), "w") as fh:
            fh.write("SECRET=must_not_commit\n")
        with open(os.path.join(self.tmpdir, ".env.example"), "w") as fh:
            fh.write("PUBLIC_TEMPLATE=\n")

        result = self._run("--fast", "--msg", VALID_MSG)
        self.assertNotIn("Falta", result.stderr)

        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        self.assertIn(".env.example", tracked)
        self.assertNotIn(".env", tracked)
        self.assertNotIn(".env.production", tracked)

    def test_push_uses_origin_upstream_when_ahead(self) -> None:
        remote = os.path.join(self.tmpdir, "remote.git")
        subprocess.run(["git", "init", "--bare", remote], check=True, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", remote], cwd=self.tmpdir, check=True, capture_output=True)

        new_file = os.path.join(self.tmpdir, "push_marker.txt")
        with open(new_file, "w") as fh:
            fh.write("push\n")
        result = self._run("--fast", "--msg", VALID_MSG)
        self.assertEqual(result.returncode, 0, result.stderr)

        upstream = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(upstream, "origin/main")


if __name__ == "__main__":
    unittest.main()
