"""
Consolidación de build de producción — identidad legal + Vite (sin pisar secretos).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class BunkerConsolidator:
    def __init__(self) -> None:
        self.root_dir = Path(__file__).resolve().parent
        self.build_dir = self.root_dir / "dist"
        manifest = self.root_dir / "production_manifest.json"
        patent = "PCT/EP2025/067317"
        siret = "94361019600017"
        if manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                patent = str(data.get("patent", patent)).strip() or patent
                siret = str(data.get("siret", siret)).strip() or siret
            except (json.JSONDecodeError, OSError):
                pass
        self.siren = siret[:9] if len(siret) >= 9 else siret
        self.patent = patent

    def clean_legacy_code(self) -> None:
        """Elimina restos opcionales de Java / carpetas legacy si existen."""
        trash = ("pom.xml", "Cola.java", "old_configs")
        print("[*] Purga de arquitectura legacy (solo si existe)...")
        for item in trash:
            path = self.root_dir / item
            if path.is_file():
                path.unlink()
                print(f"[OK] Eliminado archivo: {item}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"[OK] Eliminado directorio: {item}")

    def verify_env_variables(self) -> None:
        """Inyecta identidad legal en .env.production (merge; no borra otras claves)."""
        print("[*] Verificando credenciales de soberanía (.env.production)...")
        env_path = self.root_dir / ".env.production"
        keys = {
            "VITE_SIREN": self.siren,
            "VITE_PATENT": self.patent,
            "VITE_ENV": "PRODUCTION",
        }
        lines: list[str] = []
        if env_path.is_file():
            lines = env_path.read_text(encoding="utf-8").splitlines()
        done: set[str] = set()
        out: list[str] = []
        for ln in lines:
            s = ln.strip()
            if s and not s.startswith("#") and "=" in s:
                k = s.split("=", 1)[0].strip()
                if k in keys:
                    out.append(f"{k}={keys[k]}")
                    done.add(k)
                    continue
            out.append(ln)
        for k, v in keys.items():
            if k not in done:
                if out and out[-1].strip():
                    out.append("")
                out.append(f"# bunker_consolidator ({k})")
                out.append(f"{k}={v}")
        env_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
        print("[OK] .env.production actualizado (merge).")

    def run_build(self) -> bool:
        """Compilación Vite (usa package.json del repo)."""
        print("[*] Compilando web (npm run build)...")
        try:
            subprocess.run(
                ["npm", "run", "build"],
                check=True,
                cwd=str(self.root_dir),
            )
            print("[OK] Build finalizado. Salida en /dist")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[ERROR] Fallo en la compilación: {e}")
            return False

    def final_check(self) -> None:
        print("--- REPORTE FINAL DE SOBERANÍA ---")
        print("Estado del Búnker: OPERATIVO")
        print(f"Identidad: SIREN {self.siren} — Patente {self.patent}")
        print("Infraestructura: consolidada (revisar /dist y despliegue Vercel)")


def main() -> int:
    c = BunkerConsolidator()
    c.clean_legacy_code()
    c.verify_env_variables()
    if not c.run_build():
        return 1
    c.final_check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
