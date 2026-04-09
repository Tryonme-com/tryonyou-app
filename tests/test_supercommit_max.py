"""Tests para supercommit_max.sh — validación de sellos TryOnYou y lógica de push."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
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
        env=base_env,
    )


def _init_git_repo(path: str) -> None:
    """Initialise a minimal git repo with one initial commit."""
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@tryonyou.app"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "TryOnYou Test"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    # Initial commit so HEAD exists
    readme = os.path.join(path, "README.md")
    with open(readme, "w") as fh:
        fh.write("# test\n")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=path,
        check=True,
        capture_output=True,
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
        self.assertTrue(
            first_line.startswith("#!"),
            "Script should start with a shebang (#!)",
        )

    def test_script_uses_bash(self) -> None:
        with open(_SCRIPT) as fh:
            first_line = fh.readline()
        self.assertIn("bash", first_line)


# ---------------------------------------------------------------------------
# Stamp validation — missing stamps exit 1
# ---------------------------------------------------------------------------


class TestStampValidation(unittest.TestCase):
    """The script must reject messages that lack any required stamp."""

    def _assert_missing_stamp_exits_1(self, msg: str, description: str) -> None:
        result = _run_script(msg)
        self.assertEqual(
            result.returncode,
            1,
            f"Expected exit 1 when {description}. stderr={result.stderr!r}",
        )

    def test_missing_certeza_absoluta(self) -> None:
        msg = "Título @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"
        self._assert_missing_stamp_exits_1(msg, "missing @CertezaAbsoluta")

    def test_missing_lo_mas_erestu(self) -> None:
        msg = "Título @CertezaAbsoluta PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"
        self._assert_missing_stamp_exits_1(msg, "missing @lo+erestu")

    def test_missing_patente(self) -> None:
        msg = "Título @CertezaAbsoluta @lo+erestu Bajo Protocolo de Soberanía V10 - Founder: Rubén"
        self._assert_missing_stamp_exits_1(msg, "missing PCT/EP2025/067317")

    def test_missing_protocolo(self) -> None:
        msg = "Título @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 - Founder: Rubén"
        self._assert_missing_stamp_exits_1(msg, "missing «Bajo Protocolo de Soberanía V10»")

    def test_missing_founder(self) -> None:
        msg = "Título @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10"
        self._assert_missing_stamp_exits_1(msg, "missing «Founder: Rubén»")

    def test_empty_message_uses_default_stamps(self) -> None:
        # ${1:-default} in bash treats "" as empty → uses the built-in default.
        # The default contains all stamps, so stamp validation must pass
        # (exit code ≠ 1 means stamps were accepted).
        result = _run_script("")
        self.assertNotEqual(result.returncode, 1, "Empty-string arg should use default and pass stamp check")

    def test_missing_stamp_stderr_contains_hint(self) -> None:
        msg = "Sin sellos"
        result = _run_script(msg)
        self.assertIn("Falta", result.stderr)

    def test_all_stamps_required_together(self) -> None:
        """All stamps in the default message should pass stamp validation."""
        # We just check that we do NOT exit with error 1 due to stamp check.
        # The script will still exit ≠0 if git operations fail inside a non-git dir,
        # but the returncode should not be 1 from stamp validation alone.
        # We probe this by checking stderr does NOT mention "Falta".
        result = _run_script(VALID_MSG)
        self.assertNotIn("Falta", result.stderr)


# ---------------------------------------------------------------------------
# Default message
# ---------------------------------------------------------------------------


class TestDefaultMessage(unittest.TestCase):
    """When no argument is given the built-in default must contain all stamps."""

    def test_default_msg_does_not_fail_on_stamps(self) -> None:
        # Run without args — stamp check passes, then git may or may not fail.
        result = _run_script()
        self.assertNotIn("Falta", result.stderr)

    def test_default_msg_not_exit_1_due_to_stamps(self) -> None:
        result = _run_script()
        # Exit code 1 is exclusively from the stamp check (see script logic).
        # Any other non-zero is a git/environment error, not a stamp error.
        if result.returncode == 1:
            self.fail(
                "Default message failed stamp validation unexpectedly. "
                f"stderr={result.stderr!r}"
            )


# ---------------------------------------------------------------------------
# Commit logic in isolated git repo (no upstream)
# ---------------------------------------------------------------------------


class TestCommitLogic(unittest.TestCase):
    """Run the script in a temporary, isolated git repository."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        _init_git_repo(self.tmpdir)
        # Copy the script so it runs with its ROOT set to tmpdir
        self.script_copy = os.path.join(self.tmpdir, "supercommit_max.sh")
        shutil.copy2(_SCRIPT, self.script_copy)
        # Commit the script copy immediately so git add -A won't pick it up again
        subprocess.run(["git", "add", "supercommit_max.sh"], cwd=self.tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "add script copy"],
            cwd=self.tmpdir,
            check=True,
            capture_output=True,
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
            env={**os.environ, "HOME": self.tmpdir},
        )

    def test_nothing_to_commit_no_push_without_upstream(self) -> None:
        """With no staged changes and no upstream, script says no push."""
        result = self._run(VALID_MSG)
        combined = result.stdout + result.stderr
        # Should say no upstream or nothing to commit — not a stamp error.
        self.assertNotIn("Falta", result.stderr)
        self.assertIn("upstream", combined.lower().replace("@{u}", "upstream"))

    def test_new_file_is_committed(self) -> None:
        """A new file staged via git add -A should be committed."""
        new_file = os.path.join(self.tmpdir, "nuevo.txt")
        with open(new_file, "w") as fh:
            fh.write("hola\n")
        result = self._run(VALID_MSG)
        # Script should NOT report stamp error.
        self.assertNotIn("Falta", result.stderr)
        # Check the commit was created in the repo.
        log = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
        )
        self.assertIn("Título", log.stdout)

    def test_commit_message_contains_patente(self) -> None:
        """The commit message stored in git must include the patent reference."""
        new_file = os.path.join(self.tmpdir, "patente_test.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        self._run(VALID_MSG)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
        )
        self.assertIn("PCT/EP2025/067317", log.stdout)

    def test_commit_message_contains_certeza_absoluta(self) -> None:
        new_file = os.path.join(self.tmpdir, "certeza.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        self._run(VALID_MSG)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
        )
        self.assertIn("@CertezaAbsoluta", log.stdout)

    def test_commit_message_contains_protocolo_soberania(self) -> None:
        new_file = os.path.join(self.tmpdir, "soberania.txt")
        with open(new_file, "w") as fh:
            fh.write("data\n")
        self._run(VALID_MSG)
        log = subprocess.run(
            ["git", "log", "--format=%B", "-1"],
            cwd=self.tmpdir,
            capture_output=True,
            text=True,
        )
        self.assertIn("Bajo Protocolo de Soberanía V10", log.stdout)

    def test_no_changes_outputs_nada_nuevo(self) -> None:
        """When there is nothing to commit, the script says so."""
        result = self._run(VALID_MSG)
        self.assertIn("Nada nuevo", result.stdout)

    def test_missing_stamp_in_isolated_repo_exits_1(self) -> None:
        """Stamp check must still fail even in a clean repo."""
        result = self._run("Sin sellos aquí")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
