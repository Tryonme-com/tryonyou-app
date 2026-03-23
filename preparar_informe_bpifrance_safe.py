"""
Escribe src/modules/legal/bpifranceReport.ts (maquette dossier Bpifrance / STATION F).

No sustituye un dossier réel ni un PDF signé. Git opcional, solo ese archivo.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1, E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 preparar_informe_bpifrance_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

BPI_REPORT_TS = """/**
 * Texte de démonstration. Valider chiffres et sources avant tout dépôt Bpifrance / French Tech.
 */
export const BpifranceDossier = {
  project: "TryOnYou - L'Infrastructure de Précision",
  tech_stack: "Gemini 2.0 Flash + MediaPipe + brevet (réf. à confirmer)",
  economic_impact: "Objectif déclaré : réduction forte des retours (mesures à joindre)",
  carbon_footprint: "Impact CO₂ : à modéliser avec données opérationnelles",
  target_program: "Bourse French Tech / Aide à l'Innovation Deep Tech",
} as const;

export type BpifranceDossierManifest = typeof BpifranceDossier;

/** Ouvre l’URL du PDF résumé si VITE_BPI_EXEC_SUMMARY_URL est défini (Vercel). */
export function downloadExecutiveSummary(): void {
  const url = import.meta.env.VITE_BPI_EXEC_SUMMARY_URL ?? "";
  if (!url) {
    console.warn("Définir VITE_BPI_EXEC_SUMMARY_URL (URL publique du PDF).");
    return;
  }
  console.log("Téléchargement / ouverture du résumé exécutif…");
  window.open(url, "_blank", "noopener,noreferrer");
}
"""

GIT_PATHS = [
    "src/modules/legal/bpifranceReport.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def preparar_informe_bpifrance_safe() -> int:
    print("🇫🇷 Sincronizando maqueta dossier Bpifrance (TypeScript)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    legal_dir = os.path.join(ROOT, "src", "modules", "legal")
    os.makedirs(legal_dir, exist_ok=True)
    path = os.path.join(legal_dir, "bpifranceReport.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(BPI_REPORT_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "STRATEGY: Station F & Bpifrance Investment Dossier Hook",
        ],
        cwd=ROOT,
    )
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado. PDF y cifras reales fuera del código.")
    return 0


if __name__ == "__main__":
    sys.exit(preparar_informe_bpifrance_safe())
