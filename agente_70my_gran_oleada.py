import os
import re
from datetime import datetime, timedelta

import pandas as pd


def _nombre_archivo_seguro(empresa: str, numero: int) -> str:
    base = re.sub(r"[^\w\-]+", "_", str(empresa).strip())[:80] or "EMPRESA"
    return f"RECLAMACION_{numero:03d}_{base}.txt"


class Agente70my_GranOleada:
    def __init__(self):
        self.patente = "PCT/EP2025/067317"
        self.hoy = datetime.now()
        self.fecha_limite = (self.hoy + timedelta(days=15)).strftime("%d/%m/%Y")
        self.precio_union = "9.900 € (Precio Amigable)"
        self.archivo_leads = "TRYONYOU_CONTACTS_GLOBAL 2.xlsx - RAW_DATA.csv"

    def ejecutar_mision_40(self) -> bool:
        print("⚖️ Agente 70my: Iniciando Gran Oleada de 40 Licencias...")
        print(f"📅 Periodo de consulta abierto hasta: {self.fecha_limite}")

        try:
            df = pd.read_csv(self.archivo_leads)
            if "Tipo" not in df.columns or "Empresa" not in df.columns:
                print("❌ El CSV debe incluir columnas 'Tipo' y 'Empresa'.")
                return False

            col_contacto = "Contacto" if "Contacto" in df.columns else None

            objetivos = df[df["Tipo"].isin(["Potencial", "Contacto real"])].head(40)

            for i, (_, row) in enumerate(objetivos.iterrows(), start=1):
                contacto = row[col_contacto] if col_contacto else None
                self.sellar_y_notificar(row["Empresa"], contacto, i)

            return True
        except Exception as e:
            print(f"❌ Error al procesar la base de datos: {e}")
            return False

    def sellar_y_notificar(self, empresa, contacto, numero: int) -> None:
        if contacto is None or not pd.notnull(contacto):
            nombre_contacto = "Director de Innovación / Legal"
        else:
            raw = str(contacto).strip()
            nombre_contacto = (
                raw if raw and raw.lower() != "nan" else "Director de Innovación / Legal"
            )

        empresa_txt = str(empresa).strip() if empresa is not None and pd.notnull(empresa) else "—"

        notificacion = f"""
        REGULARIZACIÓN DE PROPIEDAD INTELECTUAL @PCT/EP2025/067317
        EXPEDIENTE: 2026-VAL-{numero:03d}
        
        EMPRESA: {empresa_txt}
        ATENCIÓN: {nombre_contacto}
        
        FECHA DE COMUNICACIÓN: {self.hoy.strftime('%d/%m/%Y')}
        FINAL DEL PERIODO DE CORTESÍA: {self.fecha_limite} (15 días naturales)
        
        PROPUESTA DE UNIÓN AMISTOSA:
        Se ofrece la regularización de su sistema de virtual try-on mediante el pago 
        único de licencia por un importe de {self.precio_union}.
        
        Tras la fecha límite, el expediente pasará a fase de reclamación judicial 
        con una base de tasación de 125.000 € por infracción detectada.
        """

        print(f"📩 [{numero}/40] Notificación sellada para {empresa_txt}. Límite: {self.fecha_limite}")

        folder = "RECLAMACIONES_40"
        os.makedirs(folder, exist_ok=True)
        fname = _nombre_archivo_seguro(empresa_txt, numero)
        path = os.path.join(folder, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(notificacion.strip() + "\n")


if __name__ == "__main__":
    Agente70my_GranOleada().ejecutar_mision_40()
