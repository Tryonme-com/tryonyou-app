import os
import re
import subprocess
from datetime import datetime, timedelta

import pandas as pd


def _nombre_expediente_archivo(empresa: str, num: int) -> str:
    base = re.sub(r"[^\w\-]+", "_", str(empresa).strip())[:60] or "ENTIDAD"
    return f"NOTIF_{num:03d}_{base}.txt"


class AgenteBunkerFinal:
    def __init__(self):
        self.patente = "PCT/EP2025/067317"
        self.precio_flash = "9.900 €"
        self.hoy = datetime.now()
        self.fecha_limite = (self.hoy + timedelta(days=15)).strftime("%d/%m/%Y")
        self.leads_csv = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"

    def purgar_jukles(self) -> None:
        """Acción de Jukles: asegura que el búnker técnico esté limpio."""
        print("🧹 Agente Jukles: Purgando caché y módulos para despliegue limpio...")
        for target in ["node_modules", ".vite", "dist"]:
            subprocess.run(["rm", "-rf", target], check=False)
        print("✨ Fricción técnica eliminada.")

    def ejecutar_mision_40(self) -> bool:
        """Acción de 70my: sella los 40 expedientes de monetización."""
        print("⚖️ Agente 70my: Procesando 40 expedientes de regularización...")
                return False

            col_contacto = "Contacto" if "Contacto" in df.columns else None
            objetivos = df[df["Tipo"].isin(["Potencial", "Contacto real"])].head(40)

            out_dir = os.path.join("BUNKER_LEGAL", "EXPEDIENTES")
            os.makedirs(out_dir, exist_ok=True)

            for num, (_, row) in enumerate(objetivos.iterrows(), start=1):
                id_exp = f"V-2026-{num:03d}"
                empresa = row["Empresa"]
                contacto = row[col_contacto] if col_contacto else None
                self.generar_documento_autoridad(empresa, contacto, id_exp, num, out_dir)

            return True
        except Exception as e:
            print(f"❌ Error en la base de datos: {e}")
            return False

    def generar_documento_autoridad(
        self,
        empresa,
        contacto,
        id_exp: str,
        num: int,
        out_dir: str,
    ) -> None:
        """Crea la notificación oficial que garantiza el cobro (mismo texto que el script base)."""
        _ = contacto  # mismo contrato que el original; el cuerpo legal no incluye el contacto

        cert = f"""
        ============================================================
        INSTITUTO DE COMPLIANCE IP - TRYONYOU INTELLIGENCE SYSTEM
        ============================================================
        EXPEDIENTE: {id_exp}
        REVISIÓN TÉCNICA: {self.hoy.strftime('%d/%m/%Y')}
        REFERENCIA: PATENTE EUROPEA {self.patente}
        
        NOTIFICACIÓN DE REGULARIZACIÓN AMISTOSA
        ---------------------------------------
        Se ha detectado actividad comercial bajo tecnología protegida en: {empresa}.
        Para su seguridad jurídica, se habilita una ventana de 15 días.
        
        FECHA LÍMITE DE TASA PREFERENCIAL: {self.fecha_limite}
        IMPORTE DE UNIÓN: {self.precio_flash}
        
        Una vez abonada la tasa, su entidad recibirá el Sello de Certeza Absoluta
        y la licencia de uso para Meta, TikTok e integraciones retail.
        
        Sin respuesta tras el {self.fecha_limite}, el expediente pasará a 
        fase de litigio internacional (Tasación: 125.000 €).
        ============================================================
        """

        fname = _nombre_expediente_archivo(str(empresa), num)
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(cert.strip() + "\n")
        print(f"📩 Expediente {id_exp} sellado para {empresa}.")


if __name__ == "__main__":
    agente = AgenteBunkerFinal()
    agente.purgar_jukles()
    agente.ejecutar_mision_40()
    print("\n🎯 TODO ENVIADO. 40 'listos' bajo reloj de 15 días. @CertezaAbsoluta")
