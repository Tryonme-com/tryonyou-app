"""
Auditoría local del repo (Git + rutas de archivos) → JSON para revisión humana o asistentes.

Qué hace de verdad: rama, último commit, comprobación de existencia de rutas clave.
Qué NO hace: no valida legalidad ante Bpifrance, no consulta Google Studio ni servidores
remotos; cualquier «confirmación legal» requiere revisión profesional y fuentes oficiales.

Salida: audit_for_yagepe.json en la raíz del repo (UTF-8).

Patente (ref.): PCT/EP2025/067317
SIRET (ref.): 94361019600017

  python3 verificador_soberano_v10.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parent


def _git(cwd: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
    )
    out = (r.stdout or r.stderr or "").strip()
    return r.returncode, out


class AuditorSoberanoV10:
    def __init__(self) -> None:
        self.patent = "PCT/EP2025/067317"
        self.siret = "94361019600017"
        self.project_id = "gen-lang-client-0091228222"
        self.root = _root()
        self.critical_files = [
            "BPI_EVIDENCE_V10.json",
            "production_manifest.json",
            "index.html",
            "scripts/verify_system.py",
        ]

    def audit_repository(self) -> int:
        print("--- Auditoría local V10 (repo + archivos) ---")

        rc_branch, branch = _git(self.root, "rev-parse", "--abbrev-ref", "HEAD")
        rc_commit, last_commit = _git(self.root, "log", "-1", "--format=%H")
        rc_dirty, dirty = _git(self.root, "status", "--porcelain")

        if rc_branch != 0:
            branch = f"(error git: {branch[:200]})"
        if rc_commit != 0:
            last_commit = f"(error git: {last_commit[:200]})"

        file_status = {f: (self.root / f).is_file() for f in self.critical_files}

        audit_report = {
            "disclaimer": "Auditoría solo local; no constituye dictamen legal ni validación Bpifrance.",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "project_reference": {
                "founder_name_ref": "Rubén Espinar Rodríguez",
                "patent_ref": self.patent,
                "siret_ref": self.siret,
            },
            "technical_anchors": {
                "project_id_ref": self.project_id,
                "repo_root": str(self.root),
                "current_branch": branch,
                "commit_hash_full": last_commit,
                "working_tree_clean": (rc_dirty == 0 and not dirty),
                "git_status_porcelain": dirty if rc_dirty == 0 else None,
                "files_verified": file_status,
            },
            "status": "LOCAL_AUDIT_COMPLETE",
        }

        out_path = self.root / "audit_for_yagepe.json"
        out_path.write_text(
            json.dumps(audit_report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        print(f"✅ Informe: {out_path.name}")
        print(
            "Revisa el JSON y el estado de Git en tu máquina; "
            "los asistentes solo pueden interpretar lo que contiene, no certificar soberanía."
        )
        return 0 if rc_branch == 0 and rc_commit == 0 else 1


if __name__ == "__main__":
    raise SystemExit(AuditorSoberanoV10().audit_repository())
