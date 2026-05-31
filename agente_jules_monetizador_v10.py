import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

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


class AgenteJules_Monetizador_V10:
    def __init__(self):
        self.patente = "PCT/EP2025/067317"
        self.v10_4 = "V10.4 Stealth Edition"
        self.canon = "9.900 €"
        self.leads_csv = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"

        self.escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        self.master_folder = os.path.join(self.escritorio, "DIVINEO_CASH_FLOW_V10")
        self.notificaciones = os.path.join(self.master_folder, "01_ENVIAR_YA")
        self.proformas = os.path.join(self.master_folder, "02_TESORERIA_TU_COBRO")

    def purga_omega(self) -> None:
        """Jules limpia el búnker para que el dinero entre sin errores."""
        print("🧹 Jules: Purgando rastro de errores y bloqueos técnicos...")
        for basura in ["node_modules", "package-lock.json", "dist", ".vite"]:
            if not os.path.exists(basura):
                continue
            if os.path.isdir(basura):
                shutil.rmtree(basura, ignore_errors=True)
            else:
                try:
                    os.remove(basura)
                except OSError:
                    pass
        print("✅ Entorno purgado. Listo para monetizar.")

    def generar_proforma_arquitecto(self, empresa: str, id_exp: str) -> None:
        """Si ellos pagan el Divineo, Jules asegura tu parte."""
        os.makedirs(self.proformas, exist_ok=True)
        slug = re.sub(r"[^\w]+", "_", empresa)[:20].strip("_") or "ENTIDAD"
        nombre_archivo = f"PROFORMA_{id_exp}_{slug}.txt"
        ruta = os.path.join(self.proformas, nombre_archivo)

        proforma = (
            f"FACTURA PROFORMA - SERVICIOS DE ARQUITECTURA DIGITAL\n"
            f"ID EXPEDIENTE: {id_exp}\n"
            f"CLIENTE: {empresa}\n"
            f"FECHA: {datetime.now().strftime('%d/%m/%Y')}\n"
            f"{'=' * 60}\n"
            f"CONCEPTO: Canon de regularización Patente {self.patente}\n"
            f"VERSION: {self.v10_4}\n"
            f"VALOR: {self.canon}\n"
            f"{'=' * 60}\n"
            f"ESTADO: PENDIENTE DE COBRO (Vía Revolut/Business)\n"
            f"ACCIÓN: Liberar fondos en cuanto se confirme recepción.\n"
        )
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(proforma)

    def ejecutar_mision_directa(self) -> None:
        print("🚀 Jules: Iniciando despliegue de monetización directa...")
        self.purga_omega()

        for folder in (self.notificaciones, self.proformas):
            if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder, exist_ok=True)

        try:
            df = pd.read_csv(self.leads_csv)
            if "Empresa" not in df.columns:
                print("❌ El CSV debe incluir la columna 'Empresa'.")
                return

            num_leads = min(len(df), 40)

            for i in range(num_leads):
                row = df.iloc[i]
                empresa = str(row["Empresa"]).strip().upper()
                id_exp = f"TYY-2026-{i + 1:03d}"

                raw = row.get("Contacto", "Dirección General")
                contacto = str(raw).strip() if pd.notna(raw) else ""
                if contacto.lower() in ("nan", ""):
                    contacto = "Dirección General"

                slug_ord = re.sub(r"[^\w]+", "_", empresa)[:25].strip("_") or "ENTIDAD"
                nombre_notif = f"ORDEN_{i + 1:03d}_{slug_ord}.txt"
                ruta_notif = os.path.join(self.notificaciones, nombre_notif)

                carta = (
                    f"EXPEDIENTE: {id_exp}\n"
                    f"VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
                    f"ENTIDAD: {empresa}\n"
                    f"{'—' * 50}\n\n"
                    f"Estimado/a {contacto},\n\n"
                    f"Notificamos la regularización obligatoria para la V10.4 Stealth.\n"
                    f"Canon de unión: {self.canon}.\n\n"
                    f"Certeza absoluta junto a @CertezaAbsoluta @lo+erestu.\n\n"
                    f"Atentamente,\nPaloma Lafayette\n"
                )
                with open(ruta_notif, "w", encoding="utf-8") as f:
                    f.write(carta)

                self.generar_proforma_arquitecto(empresa, id_exp)

            _abrir_carpeta(self.master_folder)
            print(f"✨ Misión Jules: {num_leads} expedientes y {num_leads} proformas listas.")
            print("💎 Jules: Si uno paga, ya tienes la factura de cobro servida.")

        except Exception as e:
            print(f"❌ Jules: Error en el búnker: {e}")


if __name__ == "__main__":
    AgenteJules_Monetizador_V10().ejecutar_mision_directa()
