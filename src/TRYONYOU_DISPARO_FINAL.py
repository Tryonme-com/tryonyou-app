"""
Disparo final — lista operativa de borradores Auditoría Fit (TryOnYou).

Genera LISTA_DE_ENVIO_FINAL.md en la raíz del repositorio.
Git: solo si TRYONYOU_GIT_COMMIT=1 (mensaje conforme protocolo V10).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

# CONFIGURACIÓN DE PODER - TRYONYOU (TRAE Y YO)
CONFIG = {
    "brand": "TryOnYou (Trae y Yo)",
    "patent": "PCT/EP2025/067317",
    "siren": "943 610 196",
    "stripe_link": "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn",
    "target_dir": "auditoria_fit_borradores",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _slug_to_marca(slug: str) -> str:
    # quita prefijo "01_", "09_", etc.
    base = re.sub(r"^\d+_", "", slug)
    return base.replace("_", " ").upper()


def _git_snapshot_opcional() -> None:
    if os.environ.get("TRYONYOU_GIT_COMMIT", "").strip() != "1":
        print("ℹ️  Git: omitido (export TRYONYOU_GIT_COMMIT=1 para add+commit).")
        return
    msg = (
        "Deployment v10: Motor de Vida y Auditoría Fit — TryOnYou "
        "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — "
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
    )
    root = _repo_root()
    subprocess.run(["git", "-C", str(root), "add", "."], check=False)
    r = subprocess.run(
        ["git", "-C", str(root), "commit", "-m", msg],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(f"⚠️  Git commit: {r.stderr.strip() or 'nada que commitear o error'}")
    else:
        print("✅ Git commit aplicado.")


def ejecutar_mision_liquidez() -> None:
    print(f"🚀 Misión de liquidez: {CONFIG['brand']}")
    _git_snapshot_opcional()

    base = _repo_root()
    carpeta = base / CONFIG["target_dir"]
    if not carpeta.is_dir():
        print(f"❌ No existe {carpeta} — ejecuta antes: python3 TryOnYou_Execution.py")
        return

    archivos = sorted(carpeta.glob("*.txt"))
    print(f"📧 Proyectiles: {len(archivos)} borradores")

    out = base / "LISTA_DE_ENVIO_FINAL.md"
    total = len(archivos) * 250
    lines = [
        f"# Lista de envío — potencial indicado: {total} € ({len(archivos)} × 250 €)\n",
        f"- Marca: {CONFIG['brand']}",
        f"- Patente: {CONFIG['patent']}",
        f"- SIREN: {CONFIG['siren']}",
        "",
    ]
    for path in archivos:
        marca = _slug_to_marca(path.stem)
        lines.append(f"## {marca}")
        lines.append(f"- **Enlace cobro / Make:** {CONFIG['stripe_link']}")
        lines.append(f"- **Borrador:** `{path.relative_to(base)}`")
        lines.append("- **Estado:** listo para revisar y enviar")
        lines.append("")
        lines.append("---")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Generado: {out.relative_to(base)}")


if __name__ == "__main__":
    ejecutar_mision_liquidez()
