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


class MirrorSanctuaryOrchestrator_V10_Omega:
    def __init__(self):
        # ADN Divineo: Potencia Máxima (65 Nave + 65 Jardín = 130)
        self.status = "SIMETRÍA DIVINEO ACTIVADA - FASE OMEGA (BPIFRANCE)"
        self.patente = "PCT/EP2025/067317"
        self.leads_csv = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"
        self.canon = "9.900 €"

        self.escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        self.carpeta_maestra = os.path.join(self.escritorio, "DIVINEO_V10_OMEGA")
        self.carpeta_expedientes = os.path.join(self.carpeta_maestra, "01_EXPEDIENTES_EPCT")

    def purgar_friccion(self) -> None:
        """Limpia los errores de despliegue 'rojos' de Vercel/Netlify en local."""
        print("🧹 Purga Omega: Eliminando rastro de errores y caché...")
        targets = ["node_modules", "package-lock.json", "dist", ".vite", ".next", "build"]
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
        print("✅ Entorno sanitizado. Certeza Absoluta.")

    def abrir_carpeta(self, path: str) -> None:
        """Apertura multiplataforma; usa rutas absolutas."""
        _abrir_carpeta(path)

    def ejecutar_mision_final(self) -> None:
        print(f"🚀 {self.status}")
        self.purgar_friccion()

        if os.path.exists(self.carpeta_maestra):
            shutil.rmtree(self.carpeta_maestra, ignore_errors=True)
        os.makedirs(self.carpeta_expedientes, exist_ok=True)

        try:
            if not os.path.exists(self.leads_csv):
                print(f"❌ Error: El archivo {self.leads_csv} no está en la raíz.")
                return

            df = pd.read_csv(self.leads_csv)
            if "Empresa" not in df.columns:
                print("❌ El CSV debe incluir la columna 'Empresa'.")
                return

            df = df.head(40)
            num_leads = len(df)
            fecha_vencimiento = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")

            for num, (_, row) in enumerate(df.iterrows(), start=1):
                empresa = str(row["Empresa"]).strip().upper()
                id_exp = f"TYY-2026-{num:03d}"

                raw = row.get("Contacto", "Dirección General")
                contacto = str(raw).strip() if pd.notna(raw) else ""
                if contacto.lower() in ("nan", ""):
                    contacto = "Dirección General"

                slug = re.sub(r"[^\w]+", "_", empresa)[:30].strip("_") or "ENTIDAD"
                nombre = f"ORDEN_{num:03d}_{slug}.txt"

                cuerpo = (
                    f"ORDEN DE REGULARIZACIÓN ePCT - BPIFRANCE\n"
                    f"ID EXPEDIENTE: {id_exp}\n"
                    f"VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
                    f"ENTIDAD: {empresa}\n"
                    f"REF. PATENTE: {self.patente}\n"
                    f"{'—' * 60}\n\n"
                    f"Estimado/a {contacto},\n\n"
                    f"Bajo la simetría técnica de TryOnYou Global y el respaldo de Bpifrance, "
                    f"notificamos la habilitación de su licencia para la V10.4 Stealth.\n\n"
                    f"El canon de unión de {self.canon} asegura su posición estratégica "
                    f"en el ecosistema. Fecha límite: {fecha_vencimiento}.\n\n"
                    f"Certeza absoluta junto a @CertezaAbsoluta @lo+erestu.\n\n"
                    f"Atentamente,\n\n"
                    f"Paloma Lafayette\n"
                    f"Mirror Sanctuary Orchestrator\n"
                )

                with open(
                    os.path.join(self.carpeta_expedientes, nombre),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(cuerpo)

            justificante_path = os.path.join(
                self.carpeta_maestra, "JUSTIFICANTE_REVOLUT_BPIFRANCE.txt"
            )
            with open(justificante_path, "w", encoding="utf-8") as f:
                f.write("PROYECTO: TRYONYOU GLOBAL / DIVINEO\n")
                f.write(f"ACTIVO: Patente Internacional {self.patente}\n")
                f.write("ESTADO: Cuenta Stripe Verificada por June Support.\n")
                f.write("BPIFRANCE: Seguimiento estratégico de fondos activo.\n")
                f.write("VALORACIÓN: 40 Licencias Cluster Haussmann en fase de cobro.\n")

            print(f"✨ Misión completada: {num_leads} expedientes servidos en bandeja de plata.")
            self.abrir_carpeta(self.carpeta_maestra)

        except Exception as e:
            print(f"❌ Error crítico en ejecución: {e}")

    def ejecutar_mision_paloma(self) -> None:
        self.ejecutar_mision_final()


if __name__ == "__main__":
    MirrorSanctuaryOrchestrator_V10_Omega().ejecutar_mision_final()
