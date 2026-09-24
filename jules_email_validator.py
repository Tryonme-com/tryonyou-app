import os
from datetime import datetime

import pandas as pd


class Jules_Email_Validator:
    def __init__(self):
        self.patente = "PCT/EP2025/067317"
        self.log_envios = os.path.join(os.path.expanduser("~"), "Desktop", "LOG_ENVIOS_DIVINEO.txt")
        self.archivo_leads = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"

    def validar_y_registrar(self) -> None:
        print("🔍 Jules: Validando cola de envíos para la Niña Perfecta...")

        try:
            df = pd.read_csv(self.archivo_leads).head(5)
            if "Empresa" not in df.columns:
                print("❌ El CSV debe incluir la columna 'Empresa'.")
                return

            with open(self.log_envios, "w", encoding="utf-8") as log:
                log.write(
                    f"REPORT DE ENVÍOS ePCT - {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
                    f"REF {self.patente}\n"
                )
                log.write("=" * 60 + "\n")

                for num, (_, row) in enumerate(df.iterrows(), start=1):
                    empresa = str(row["Empresa"]).strip().upper()
                    raw = row.get("Email", "contacto@empresa.com")
                    email = str(raw).strip() if pd.notna(raw) else ""
                    if email.lower() in ("nan", ""):
                        email = "contacto@empresa.com"

                    id_exp = f"TYY-2026-{num:03d}"

                    registro = (
                        f"[{datetime.now().strftime('%H:%M:%S')}] ID: {id_exp} | "
                        f"DESTINATARIO: {email} | EMPRESA: {empresa} | "
                        f"ESTADO: LISTO PARA DISPARO (V10.4 Stealth)\n"
                    )
                    log.write(registro)
                    print(f"✅ Prueba generada para: {empresa}")

            print("\n✨ Jules: Prueba completada. El log de envíos está en tu Escritorio.")
            print(f"📎 Archivo: {self.log_envios}")

        except Exception as e:
            print(f"❌ Error en la prueba de Jules: {e}")


if __name__ == "__main__":
    Jules_Email_Validator().validar_y_registrar()
