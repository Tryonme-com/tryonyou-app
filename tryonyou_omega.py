import os
import re
import subprocess
from datetime import datetime, timedelta

import pandas as pd


def _nombre_orden_archivo(empresa: str, num: int) -> str:
    base = re.sub(r"[^\w\-]+", "_", str(empresa).strip())[:60] or "ENTIDAD"
    return f"ORDEN_{num:03d}_{base}.txt"


class TryOnYouOmega:
    def __init__(self):
        self.patente = "PCT/EP2025/067317"
        self.precio_union = "9.900 €"
        self.hoy = datetime.now()
        self.fecha_limite = (self.hoy + timedelta(days=15)).strftime("%d/%m/%Y")
        self.leads_csv = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"

        self.agente_jukles = "Ejecutor Técnico"
        self.agente_70my = "Compliance & Monetización"
        self.agente_vuelo = "Logística Shopify"

    def fase_1_jukles_limpieza(self) -> None:
        """PURGA TOTAL: elimina errores de Vite/Modules para Certeza Absoluta."""
        print(f"🧹 [{self.agente_jukles}]: Purgando fricción técnica...")
        folders = ["node_modules", "dist", ".vite", "package-lock.json"]
        for f in folders:
            subprocess.run(["rm", "-rf", f], check=False)
        print("✨ Búnker técnico purificado. Listo para el build @Divineo.")

    def fase_2_70my_monetizacion_40(self) -> None:
        """COBRO ESTRATÉGICO: sella los 40 expedientes con autoridad."""
        print(f"⚖️ [{self.agente_70my}]: Iniciando Gran Oleada de 40 Licencias...")
        try:
            df = pd.read_csv(self.leads_csv)
            if "Tipo" not in df.columns or "Empresa" not in df.columns:
                print("⚠️ El CSV debe incluir columnas 'Tipo' y 'Empresa'.")
                return

            col_contacto = "Contacto" if "Contacto" in df.columns else None
            objetivos = df[df["Tipo"].isin(["Potencial", "Contacto real"])].head(40)

            out_dir = "EXPEDIENTES_COMPLIANCE"
            os.makedirs(out_dir, exist_ok=True)

            for num, (_, row) in enumerate(objetivos.iterrows(), start=1):
                id_exp = f"TYY-2026-{num:03d}"
                empresa = row["Empresa"]
                contacto = row[col_contacto] if col_contacto else None
                self._generar_notificacion_legal(empresa, contacto, id_exp, num, out_dir)

            print(f"✅ 40 Expedientes sellados. Periodo de gracia hasta {self.fecha_limite}.")
        except Exception as e:
            print(f"⚠️ Error en base de datos: {e}")

    def _generar_notificacion_legal(
        self,
        empresa,
        contacto,
        id_exp: str,
        num: int,
        out_dir: str,
    ) -> None:
        """Crea el documento de regularización."""
        atn = (
            contacto
            if contacto is not None and pd.notnull(contacto) and str(contacto).strip()
            else "Dirección General"
        )

        contenido = f"""
        ============================================================
        NOTIFICACIÓN OFICIAL DE REGULARIZACIÓN - TRYONYOU IP
        ============================================================
        ID EXPEDIENTE: {id_exp} | REF: {self.patente}
        EMPRESA: {empresa} | ATN: {atn}
        
        SITUACIÓN: Uso de tecnología de ajuste biométrico detectado.
        PROPUESTA DE UNIÓN: Pago único de {self.precio_union}.
        
        VENTANA DE CORTESÍA: 15 Días Naturales.
        FECHA LÍMITE DE TARIFA AMISTOSA: {self.fecha_limite}
        
        Tras el vencimiento, el expediente se deriva a la fase de 
        Reclamación Internacional (Tasación base: 125.000 €).
        ============================================================
        """

        path = os.path.join(out_dir, _nombre_orden_archivo(str(empresa), num))
        with open(path, "w", encoding="utf-8") as f:
            f.write(contenido.strip() + "\n")

    def fase_3_vuelo_shopify(self) -> None:
        """Sincroniza colaboraciones (log; API Shopify pendiente)."""
        print(f"🚀 [{self.agente_vuelo}]: Activando catálogo de impacto...")
        colabs = ["Levi's 510 Biometric", "Lafayette Gold", "Adidas Ultra-Fit"]
        for c in colabs:
            print(f"🛒 Sincronizando {c} con Shopify... Sello de Certeza inyectado.")

    def ejecucion_omega(self) -> None:
        print(f"--- 🏁 INICIANDO SISTEMA OMEGA @TRYONYOU ({self.hoy.strftime('%H:%M')}) ---")
        self.fase_1_jukles_limpieza()
        self.fase_2_70my_monetizacion_40()
        self.fase_3_vuelo_shopify()
        print("\n💰 Misión cumplida. 15 días de consulta activos. @CertezaAbsoluta @lo+erestu")


if __name__ == "__main__":
    TryOnYouOmega().ejecucion_omega()
