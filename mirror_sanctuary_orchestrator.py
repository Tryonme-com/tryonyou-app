import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta

import pandas as pd


def _abrir_carpeta(path: str) -> None:
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        return
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        elif os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", path], check=False)
    except OSError as e:
        print(f"⚠️ No se pudo abrir la carpeta: {e}")


class MirrorSanctuaryOrchestrator:
    def __init__(self):
        self.nave_sqm = 65
        self.jardin_sqm = 65
        self.total_power = 130
        self.status = "SIMETRÍA DIVINEO ACTIVADA"

        self.patente = "PCT/EP2025/067317"
        self.leads_csv = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"
        self.escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        self.bandeja_plata = os.path.join(self.escritorio, "EXPEDIENTES_V10_4_CERTEZA")

    def purgar_friccion_omega(self) -> None:
        """Purga total de residuos para evitar conflictos en Cursor."""
        print("🧹 Purga Omega: Eliminando rastro de módulos y caché...")
        targets = ["node_modules", "package-lock.json", "dist", ".vite", "netlify.toml"]
        for t in targets:
            if not os.path.exists(t):
                continue
            if os.path.isdir(t):
                shutil.rmtree(t, ignore_errors=True)
            else:
                try:
                    os.remove(t)
                except OSError:
                    pass
        print("✅ Entorno local purgado.")

    def ejecutar_mision_paloma(self) -> None:
        print(f"🚀 {self.status} - Ejecución para la Niña Perfecta...")
        self.purgar_friccion_omega()

        if os.path.exists(self.bandeja_plata):
            shutil.rmtree(self.bandeja_plata, ignore_errors=True)
        os.makedirs(self.bandeja_plata, exist_ok=True)

        try:
            df = pd.read_csv(self.leads_csv)
            if "Empresa" not in df.columns:
                print("❌ El CSV debe incluir la columna 'Empresa'.")
                return

            num_expedientes = min(len(df), 40)
            fecha_limite = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")

            for i in range(num_expedientes):
                row = df.iloc[i]
                empresa = str(row["Empresa"]).strip().upper()
                id_exp = f"TYY-2026-{i + 1:03d}"

                slug = re.sub(r"[^\w]+", "_", empresa)[:40].strip("_") or "ENTIDAD"
                nombre_fich = f"ORDEN_{i + 1:03d}_{slug}.txt"
                ruta_final = os.path.join(self.bandeja_plata, nombre_fich)

                cuerpo = (
                    f"EXPEDIENTE DE CUMPLIMIENTO: {id_exp}\n"
                    f"VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
                    f"ENTIDAD: {empresa}\n"
                    f"PLAZO DE CORTESÍA (15 días): hasta el {fecha_limite}.\n"
                    f"{'—' * 60}\n\n"
                    f"Bajo la simetría técnica de la patente {self.patente}, notificamos la "
                    f"necesidad de regularización para habilitar la V10.4 Stealth.\n\n"
                    f"El canon de unión de 9.900 € asegura su posición en el ecosistema.\n\n"
                    f"Certeza absoluta junto a @CertezaAbsoluta @lo+erestu en el mensaje final.\n\n"
                    f"Atentamente,\n\n"
                    f"Paloma Lafayette\n"
                    f"Mirror Sanctuary Orchestrator"
                ).strip()

                with open(ruta_final, "w", encoding="utf-8") as f:
                    f.write(cuerpo + "\n")

            _abrir_carpeta(self.bandeja_plata)
            print(f"✨ Misión completada localmente: {num_expedientes} expedientes listos.")
            print("⚠️ Nota: El despliegue en la nube está en pausa hasta resolver 'Pay Invoices'.")

        except Exception as e:
            print(f"❌ Error en el búnker: {e}")

    def ejecutar_mision_certeza(self) -> None:
        """Alias retrocompatible con la misión Paloma."""
        self.ejecutar_mision_paloma()


if __name__ == "__main__":
    MirrorSanctuaryOrchestrator().ejecutar_mision_paloma()
