"""
Sincronización conservadora con GitHub — sin token en la URL de remote, sin reset destructivo por defecto.

Evita el antipatrón REPO_URL = f"https://{TOKEN}@github.com/..." (el token acaba en .git/config y en logs).

Recomendado:
  - Remote SSH: git@github.com:tryonme-com/tryonyou-app.git
  - O HTTPS sin credenciales en URL + `gh auth login` / credential helper.

Variables:
  GITHUB_TOKEN — solo para comprobar API (Authorization: Bearer); no modifica git remote.
  BUNKER_GIT_PATHS — rutas separadas por coma a incluir en `git add` (obligatorio si BUNKER_GIT_SYNC=1).
  BUNKER_GIT_SYNC=1 — ejecuta add + commit + push (sin `git add .`).
  BUNKER_GIT_BRANCH — rama destino (default: main).

Nunca hace `git reset --hard` ni `git clean -fd` salvo BUNKER_GIT_DESTRUCTIVE_CLEAN=1 (explícito).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import subprocess
import sys
import urllib.error
import urllib.request


def _run(cmd: list[str], *, cwd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def verify_github_token() -> bool:
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if not tok:
        print("GITHUB_TOKEN no definido: omisión verificación API.", file=sys.stderr)
        return False
    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {tok}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            del r
        print("OK — GITHUB_TOKEN válido frente a api.github.com (no se ha tocado git remote).")
        return True
    except urllib.error.HTTPError as e:
        print(f"GitHub API HTTP {e.code}: token inválido o sin permisos.", file=sys.stderr)
        return False
    except OSError as e:
        print(f"Red / API: {e}", file=sys.stderr)
        return False


def destructive_clean_allowed() -> bool:
    return os.environ.get("BUNKER_GIT_DESTRUCTIVE_CLEAN", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def optional_destructive_clean(root: str) -> None:
    if not destructive_clean_allowed():
        return
    print("⚠️  BUNKER_GIT_DESTRUCTIVE_CLEAN=1 → git reset --hard + clean -fd")
    _run(["git", "reset", "--hard", "HEAD"], cwd=root)
    _run(["git", "clean", "-fd"], cwd=root)


def sync_selective(root: str) -> int:
    if os.environ.get("BUNKER_GIT_SYNC", "").strip() != "1":
        print("Define BUNKER_GIT_SYNC=1 para add/commit/push selectivo.")
        return 0
    raw = os.environ.get("BUNKER_GIT_PATHS", "").strip()
    if not raw:
        print(
            "BUNKER_GIT_PATHS vacío: lista rutas separadas por coma (no se usa `git add .`).",
            file=sys.stderr,
        )
        return 2
    paths = [p.strip() for p in raw.split(",") if p.strip()]
    for p in paths:
        fp = os.path.join(root, p) if not os.path.isabs(p) else p
        if p.endswith(".env") or "/.env" in p.replace("\\", "/"):
            print(f"Rechazado: no se versiona .env ({p}).", file=sys.stderr)
            return 3
    branch = os.environ.get("BUNKER_GIT_BRANCH", "main").strip() or "main"
    msg = os.environ.get(
        "BUNKER_GIT_COMMIT_MSG",
        "CORE: consolidación selectiva | @CertezaAbsoluta @lo+erestu PCT/EP2025/067317",
    ).strip()
    sub = (
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
    )

    r = _run(["git", "add", *paths], cwd=root)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return 4
    r = _run(["git", "commit", "-m", msg, "-m", sub], cwd=root)
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr).lower():
        print(r.stderr or r.stdout, file=sys.stderr)
        return 5
    r = _run(["git", "push", "origin", branch], cwd=root)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return 6
    print(f"Push a origin/{branch} completado (rutas acotadas).")
    return 0


def main() -> int:
    root = os.path.abspath(os.environ.get("BUNKER_PROJECT_ROOT", os.getcwd()))
    if not os.path.isdir(os.path.join(root, ".git")):
        print(f"No hay .git en {root}", file=sys.stderr)
        return 1
    verify_github_token()
    optional_destructive_clean(root)
    return sync_selective(root)


if __name__ == "__main__":
    raise SystemExit(main())
