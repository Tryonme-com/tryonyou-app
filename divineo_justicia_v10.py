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


class Divineo_Justicia_V10:
    def __init__(self):
        self.status = "SIMETRÍA DIVINEO - FASE 2: CERTEZA ABSOLUTA"
        self.patente = "PCT/EP2025/067317"
        self.canon = "9.900 €"
        self.escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        self.carpeta_entrega = os.path.join(self.escritorio, "DIVINEO_EPCT_V10_4")
        self.leads_csv = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"

    def purga_omega_total(self) -> None:
        """Limpia el entorno para que el despliegue sea impecable post-pago."""
        print("🧹 Purga Omega: Eliminando rastro de fricción técnica...")
        targets = ["node_modules", "package-lock.json", "dist", ".vite"]
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
        print("✅ Bunker sanitizado. Listos para vivir el Divineo.")

    def servir_bandeja_plata(self) -> None:
        print(f"🚀 {self.status}")
        self.purga_omega_total()

        if os.path.exists(self.carpeta_entrega):
            shutil.rmtree(self.carpeta_entrega, ignore_errors=True)
        os.makedirs(self.carpeta_entrega, exist_ok=True)

        try:
            df_full = pd.read_csv(self.leads_csv)
            if "Empresa" not in df_full.columns:
                print("❌ El CSV debe incluir la columna 'Empresa'.")
                return

            df = df_full.head(40)
            fecha_limite = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")
            n = len(df)

            for num, (_, row) in enumerate(df.iterrows(), start=1):
                empresa = str(row["Empresa"]).strip().upper()
                id_exp = f"TYY-2026-{num:03d}"

                slug = re.sub(r"[^\w]+", "_", empresa)[:30].strip("_") or "ENTIDAD"
                nombre_fich = f"ORDEN_{num:03d}_{slug}.txt"

                cuerpo = (
                    f"EXPEDIENTE ePCT: {id_exp}\n"
                    f"VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
                    f"ENTIDAD: {empresa}\n"
                    f"PLAZO DE CORTESÍA (15 días): hasta el {fecha_limite}.\n"
                    f"{'—' * 60}\n\n"
                    f"Estimados,\n\n"
                    f"Bajo la simetría técnica de la patente {self.patente}, notificamos la "
                    f"necesidad de regularización para habilitar su acceso a la V10.4 Stealth.\n\n"
                    f"Este canon de unión de {self.canon} asegura su posición en el ecosistema "
                    f"y respeta el valor del trabajo del arquitecto original.\n\n"
                    f"Certeza absoluta junto a @CertezaAbsoluta @lo+erestu en el mensaje final.\n\n"
                    f"Atentamente,\n\n"
                    f"Paloma Lafayette\n"
                    f"Mirror Sanctuary Orchestrator\n"
                )

                path = os.path.join(self.carpeta_entrega, nombre_fich)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(cuerpo)

            print(f"✅ ¡Éxito! {n} expedientes servidos en el escritorio. Es justo y necesario.")
            _abrir_carpeta(self.carpeta_entrega)

        except Exception as e:
            print(f"❌ Error en la bandeja de plata: {e}")


if __name__ == "__main__":
    Divineo_Justicia_V10().servir_bandeja_plata()
